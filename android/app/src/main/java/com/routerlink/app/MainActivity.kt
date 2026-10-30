package com.routerlink.app

import android.app.Activity
import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.runtime.*
import com.google.zxing.integration.android.IntentIntegrator
import com.routerlink.app.ui.screens.*
import com.routerlink.app.ui.theme.RouterLinkTheme
import com.routerlink.app.ui.viewmodel.MainViewModel
import org.json.JSONObject

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    private val vpnPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            viewModel.toggleVpn()
        } else {
            Toast.makeText(this, "VPN permission is required to establish tunnel", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            RouterLinkTheme {
                var currentScreen by remember { mutableStateOf("home") }

                if (!viewModel.isLoggedIn) {
                    LoginScreen(
                        viewModel = viewModel,
                        onScanQrClicked = { startQrScanner() }
                    )
                } else {
                    when (currentScreen) {
                        "protocols" -> ProtocolsScreen(
                            viewModel = viewModel,
                            onBack = { currentScreen = "home" }
                        )
                        "diagnostics" -> DiagnosticsScreen(
                            viewModel = viewModel,
                            onBack = { currentScreen = "home" }
                        )
                        else -> HomeScreen(
                            viewModel = viewModel,
                            onNavigateProtocols = { currentScreen = "protocols" },
                            onNavigateDiagnostics = { currentScreen = "diagnostics" },
                            onLogout = { viewModel.logout() }
                        )
                    }
                }
            }
        }
    }

    fun requestVpnPermissionAndConnect() {
        val intent = VpnService.prepare(this)
        if (intent != null) {
            vpnPermissionLauncher.launch(intent)
        } else {
            viewModel.toggleVpn()
        }
    }

    private fun startQrScanner() {
        val integrator = IntentIntegrator(this)
        integrator.setPrompt("Scan RouterLink Connection QR Code")
        integrator.setBeepEnabled(true)
        integrator.setOrientationLocked(false)
        integrator.initiateScan()
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        val result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (result != null && result.contents != null) {
            try {
                val json = JSONObject(result.contents)
                val server = json.optString("server", "")
                val port = json.optInt("port", 8080)
                val user = json.optString("username", "")

                if (server.isNotEmpty()) {
                    viewModel.repository.updateServerUrl("http://$server:$port")
                    Toast.makeText(this, "Server configured for user $user", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this, "Invalid QR code payload", Toast.LENGTH_SHORT).show()
            }
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }
}

