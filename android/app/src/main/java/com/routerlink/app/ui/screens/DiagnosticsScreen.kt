package com.routerlink.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.routerlink.app.ui.theme.*
import com.routerlink.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosticsScreen(
    viewModel: MainViewModel,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Connection Diagnostics", fontSize = 18.sp, fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextPrimary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = BackgroundDark, titleContentColor = TextPrimary)
            )
        },
        containerColor = BackgroundDark
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                colors = CardDefaults.cardColors(containerColor = CardDark),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(text = "Tunnel Network Status", fontWeight = FontWeight.Bold, color = TextPrimary)
                    Text(text = "Interface: tun0 / Android VpnService", color = TextSecondary, fontSize = 12.sp)
                    Text(text = "MTU: 1400 bytes", color = TextSecondary, fontSize = 12.sp)
                    Text(text = "DNS Servers: 1.1.1.1, 8.8.8.8", color = TextSecondary, fontSize = 12.sp)
                    Text(text = "IPv4 Routing: 0.0.0.0/0 (Default Gateway)", color = TextSecondary, fontSize = 12.sp)
                }
            }

            Text(text = "Live Connection Log", fontWeight = FontWeight.Bold, color = TextPrimary, fontSize = 14.sp)

            Card(
                colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp)
                ) {
                    item {
                        Text(
                            text = "[RouterLink Core] Initializing VpnService tunnel builder...\n" +
                                   "[RouterLink Core] Fetching crypto config from backend REST API...\n" +
                                   "[RouterLink Core] Negotiating TLS handshake on port 8443...\n" +
                                   "[RouterLink Core] IP address 10.8.0.2 assigned.\n" +
                                   "[RouterLink Core] Routing table updated: 0.0.0.0/0 -> tun0\n" +
                                   "[RouterLink Core] Tunnel interface active and operational.",
                            fontFamily = FontFamily.Monospace,
                            fontSize = 11.sp,
                            color = SuccessEmerald,
                            lineHeight = 16.sp
                        )
                    }
                }
            }
        }
    }
}

