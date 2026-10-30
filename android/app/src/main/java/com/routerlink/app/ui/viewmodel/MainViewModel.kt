package com.routerlink.app.ui.viewmodel

import android.app.Application
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.routerlink.app.data.model.UserProfile
import com.routerlink.app.data.model.VpnProtocol
import com.routerlink.app.data.model.VpnStatus
import com.routerlink.app.data.repository.RouterLinkRepository
import com.routerlink.app.vpn.RouterLinkVpnService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {

    val repository = RouterLinkRepository(application)

    val vpnStatus: StateFlow<VpnStatus> = RouterLinkVpnService.vpnStatus
    val downloadSpeed: StateFlow<Long> = RouterLinkVpnService.downloadSpeedBytesPerSec
    val uploadSpeed: StateFlow<Long> = RouterLinkVpnService.uploadSpeedBytesPerSec
    val totalUploaded: StateFlow<Long> = RouterLinkVpnService.totalBytesUploaded
    val totalDownloaded: StateFlow<Long> = RouterLinkVpnService.totalBytesDownloaded
    val durationSeconds: StateFlow<Long> = RouterLinkVpnService.connectionDurationSeconds

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    val isLoggedIn: Boolean
        get() = repository.authToken != null

    init {
        if (isLoggedIn) {
            refreshProfile()
        }
    }

    fun login(username: String, pass: String, serverUrl: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            repository.updateServerUrl(serverUrl)

            val result = repository.login(username, pass)
            _isLoading.value = false

            if (result.isSuccess) {
                refreshProfile()
            } else {
                _errorMessage.value = result.exceptionOrNull()?.message ?: "Login failed"
            }
        }
    }

    fun refreshProfile() {
        viewModelScope.launch {
            val res = repository.fetchProfile()
            if (res.isSuccess) {
                _userProfile.value = res.getOrNull()
            }
        }
    }

    fun setProtocol(protocol: VpnProtocol) {
        repository.selectedProtocol = protocol
    }

    fun toggleVpn() {
        val context = getApplication<Application>()
        if (vpnStatus.value == VpnStatus.CONNECTED || vpnStatus.value == VpnStatus.CONNECTING) {
            val intent = Intent(context, RouterLinkVpnService::class.java).apply {
                action = RouterLinkVpnService.ACTION_DISCONNECT
            }
            context.startService(intent)
        } else {
            val intent = Intent(context, RouterLinkVpnService::class.java).apply {
                action = RouterLinkVpnService.ACTION_CONNECT
            }
            context.startService(intent)
        }
    }

    fun logout() {
        if (vpnStatus.value == VpnStatus.CONNECTED) {
            toggleVpn()
        }
        repository.logout()
        _userProfile.value = null
    }
}

