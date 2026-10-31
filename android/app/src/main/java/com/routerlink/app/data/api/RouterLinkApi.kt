package com.routerlink.app.data.api

import com.routerlink.app.data.model.*
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.*

interface RouterLinkApi {

    @POST("api/v1/client/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<TokenResponse>

    @GET("api/v1/client/profile")
    suspend fun getProfile(
        @Header("Authorization") token: String
    ): Response<UserProfile>

    @GET("api/v1/client/config/openvpn")
    suspend fun getOpenVpnConfig(
        @Header("Authorization") token: String,
        @Query("proto") proto: String = "tcp"
    ): Response<ResponseBody>

    @GET("api/v1/client/config/wireguard")
    suspend fun getWireGuardConfig(
        @Header("Authorization") token: String
    ): Response<ResponseBody>

    @GET("api/v1/client/config/ikev2")
    suspend fun getIkeV2Config(
        @Header("Authorization") token: String
    ): Response<ResponseBody>

    @POST("api/v1/client/heartbeat")
    suspend fun sendHeartbeat(
        @Header("Authorization") token: String,
        @Body request: HeartbeatRequest
    ): Response<HeartbeatResponse>
}

