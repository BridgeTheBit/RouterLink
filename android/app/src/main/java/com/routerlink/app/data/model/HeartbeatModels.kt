package com.routerlink.app.data.model

import com.google.gson.annotations.SerializedName

data class HeartbeatRequest(
    @SerializedName("session_token") val sessionToken: String?,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("device_name") val deviceName: String = "Android Device",
    val protocol: String,
    @SerializedName("upload_delta_bytes") val uploadDeltaBytes: Long = 0,
    @SerializedName("download_delta_bytes") val downloadDeltaBytes: Long = 0
)

data class HeartbeatResponse(
    @SerializedName("session_token") val sessionToken: String,
    @SerializedName("can_continue") val canContinue: Boolean,
    val status: String,
    @SerializedName("remaining_traffic_bytes") val remainingTrafficBytes: Long?,
    @SerializedName("used_traffic_bytes") val usedTrafficBytes: Long,
    @SerializedName("is_expired") val isExpired: Boolean
)

