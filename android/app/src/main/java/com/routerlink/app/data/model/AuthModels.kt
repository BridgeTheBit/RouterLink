package com.routerlink.app.data.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val username: String,
    val password: String
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    val role: String,
    val username: String,
    @SerializedName("expires_in") val expiresIn: Long
)

data class UserProfile(
    val id: Int,
    val username: String,
    val email: String?,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("traffic_limit_bytes") val trafficLimitBytes: Long,
    @SerializedName("used_traffic_bytes") val usedTrafficBytes: Long,
    @SerializedName("remaining_traffic_bytes") val remainingTrafficBytes: Long?,
    @SerializedName("is_expired") val isExpired: Boolean,
    @SerializedName("is_quota_depleted") val isQuotaDepleted: Boolean,
    @SerializedName("can_connect") val canConnect: Boolean,
    @SerializedName("expires_at") val expiresAt: String?,
    @SerializedName("max_concurrent_connections") val maxConcurrentConnections: Int,
    @SerializedName("allowed_protocols") val allowedProtocols: String
)

enum class VpnProtocol(val id: String, val displayName: String, val port: Int, val description: String) {
    OPENVPN_TCP("openvpn_tcp", "OpenVPN (TCP)", 8443, "Port 8443 • Anti-censorship / TLS"),
    OPENVPN_UDP("openvpn_udp", "OpenVPN (UDP)", 1194, "Port 1194 • High Speed / UDP"),
    WIREGUARD("wireguard", "WireGuard (UDP)", 51820, "Port 51820 • High Speed / Modern"),
    IKEV2("ikev2", "IKEv2/IPSec (UDP)", 500, "Port 500 • Native iOS & Android Support")
}

enum class VpnStatus {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    RECONNECTING,
    FAILED
}

