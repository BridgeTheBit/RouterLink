package com.routerlink.app.data.repository

import android.content.Context
import android.content.SharedPreferences
import com.routerlink.app.data.api.ApiClient
import com.routerlink.app.data.api.RouterLinkApi
import com.routerlink.app.data.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.UUID

class RouterLinkRepository(private val context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("routerlink_prefs", Context.MODE_PRIVATE)

    var serverUrl: String
        get() = prefs.getString("server_url", "http://192.168.88.1:8080") ?: "http://192.168.88.1:8080"
        set(value) = prefs.edit().putString("server_url", value).apply()

    var authToken: String?
        get() = prefs.getString("auth_token", null)
        set(value) = prefs.edit().putString("auth_token", value).apply()

    var currentUsername: String?
        get() = prefs.getString("current_username", null)
        set(value) = prefs.edit().putString("current_username", value).apply()

    var selectedProtocol: VpnProtocol
        get() {
            val saved = prefs.getString("selected_protocol", VpnProtocol.OPENVPN_TCP.name)
            return try { VpnProtocol.valueOf(saved!!) } catch (e: Exception) { VpnProtocol.OPENVPN_TCP }
        }
        set(value) = prefs.edit().putString("selected_protocol", value.name).apply()

    val deviceId: String
        get() {
            var id = prefs.getString("device_id", null)
            if (id == null) {
                id = UUID.randomUUID().toString()
                prefs.edit().putString("device_id", id).apply()
            }
            return id
        }

    private var api: RouterLinkApi = ApiClient.create(serverUrl)

    fun updateServerUrl(url: String) {
        serverUrl = url
        api = ApiClient.create(url)
    }

    suspend fun login(username: String, pass: String): Result<TokenResponse> = withContext(Dispatchers.IO) {
        try {
            val res = api.login(LoginRequest(username, pass))
            if (res.isSuccessful && res.body() != null) {
                authToken = res.body()!!.accessToken
                currentUsername = res.body()!!.username
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Login failed: ${res.code()} - ${res.errorBody()?.string()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchProfile(): Result<UserProfile> = withContext(Dispatchers.IO) {
        val token = authToken ?: return@withContext Result.failure(Exception("Not authenticated"))
        try {
            val res = api.getProfile("Bearer $token")
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch profile: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchVpnConfig(protocol: VpnProtocol): Result<String> = withContext(Dispatchers.IO) {
        val token = authToken ?: return@withContext Result.failure(Exception("Not authenticated"))
        try {
            val res = if (protocol == VpnProtocol.WIREGUARD) {
                api.getWireGuardConfig("Bearer $token")
            } else {
                val protoParam = if (protocol == VpnProtocol.OPENVPN_UDP) "udp" else "tcp"
                api.getOpenVpnConfig("Bearer $token", protoParam)
            }
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!.string())
            } else {
                Result.failure(Exception("Failed to fetch VPN config: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendHeartbeat(
        sessionToken: String?,
        uploadDelta: Long,
        downloadDelta: Long
    ): Result<HeartbeatResponse> = withContext(Dispatchers.IO) {
        val token = authToken ?: return@withContext Result.failure(Exception("Not authenticated"))
        try {
            val req = HeartbeatRequest(
                sessionToken = sessionToken,
                deviceId = deviceId,
                deviceName = "${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}",
                protocol = selectedProtocol.id,
                uploadDeltaBytes = uploadDelta,
                downloadDeltaBytes = downloadDelta
            )
            val res = api.sendHeartbeat("Bearer $token", req)
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Heartbeat failed: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        authToken = null
        currentUsername = null
        prefs.edit().remove("auth_token").remove("current_username").apply()
    }
}

