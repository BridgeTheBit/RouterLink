package com.routerlink.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.routerlink.app.data.model.VpnProtocol
import com.routerlink.app.ui.theme.*
import com.routerlink.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProtocolsScreen(
    viewModel: MainViewModel,
    onBack: () -> Unit
) {
    val selected = viewModel.repository.selectedProtocol
    val protocols = listOf(
        VpnProtocol.OPENVPN_TCP,
        VpnProtocol.WIREGUARD,
        VpnProtocol.OPENVPN_UDP
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("VPN Protocol Selection", fontSize = 18.sp, fontWeight = FontWeight.Bold) },
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(protocols) { proto ->
                val isCurrent = proto == selected
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isCurrent) CardDark else SurfaceDark
                    ),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            viewModel.setProtocol(proto)
                            onBack()
                        }
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = proto.displayName,
                                color = TextPrimary,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Port ${proto.port} • ${if (proto == VpnProtocol.OPENVPN_TCP) "Anti-censorship / TLS" else "High Speed / UDP"}",
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }
                        if (isCurrent) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessEmerald)
                        }
                    }
                }
            }
        }
    }
}

