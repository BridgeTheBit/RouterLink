package com.routerlink.app.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.routerlink.app.data.model.VpnStatus
import com.routerlink.app.ui.theme.*
import com.routerlink.app.ui.viewmodel.MainViewModel

@Composable
fun HomeScreen(
    viewModel: MainViewModel,
    onNavigateProtocols: () -> Unit,
    onNavigateDiagnostics: () -> Unit,
    onLogout: () -> Unit
) {
    val status by viewModel.vpnStatus.collectAsState()
    val downloadSpeed by viewModel.downloadSpeed.collectAsState()
    val uploadSpeed by viewModel.uploadSpeed.collectAsState()
    val durationSeconds by viewModel.durationSeconds.collectAsState()
    val profile by viewModel.userProfile.collectAsState()

    val isConnected = status == VpnStatus.CONNECTED
    val isConnecting = status == VpnStatus.CONNECTING

    // Pulsing animation for active tunnel
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isConnected) 1.08f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        // Top Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "RouterLink",
                    color = TextPrimary,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Gateway: ${viewModel.repository.serverUrl.replace("http://", "").replace("https://", "")}",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                IconButton(onClick = onNavigateDiagnostics) {
                    Icon(Icons.Default.Build, contentDescription = "Diagnostics", tint = TextSecondary)
                }
                IconButton(onClick = onLogout) {
                    Icon(Icons.Default.ExitToApp, contentDescription = "Logout", tint = TextSecondary)
                }
            }
        }

        // Center Connect Button
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(vertical = 16.dp)
        ) {
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .size(200.dp)
                    .scale(pulseScale)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = if (isConnected) listOf(SuccessEmerald.copy(alpha = 0.3f), Color.Transparent)
                            else if (isConnecting) listOf(WarningAmber.copy(alpha = 0.3f), Color.Transparent)
                            else listOf(BrandPrimary.copy(alpha = 0.15f), Color.Transparent)
                        )
                    )
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(150.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.linearGradient(
                                colors = if (isConnected) listOf(SuccessEmerald, Color(0xFF059669))
                                else if (isConnecting) listOf(WarningAmber, Color(0xFFD97706))
                                else listOf(BrandPrimary, BrandSecondary)
                            )
                        )
                        .clickable { viewModel.toggleVpn() }
                ) {
                    Icon(
                        imageVector = Icons.Default.PowerSettingsNew,
                        contentDescription = "Connect Toggle",
                        tint = Color.white,
                        modifier = Modifier.size(60.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = when (status) {
                    VpnStatus.CONNECTED -> "CONNECTED"
                    VpnStatus.CONNECTING -> "CONNECTING..."
                    VpnStatus.RECONNECTING -> "RECONNECTING..."
                    VpnStatus.FAILED -> "CONNECTION FAILED"
                    VpnStatus.DISCONNECTED -> "NOT CONNECTED"
                },
                color = when (status) {
                    VpnStatus.CONNECTED -> SuccessEmerald
                    VpnStatus.CONNECTING, VpnStatus.RECONNECTING -> WarningAmber
                    VpnStatus.FAILED -> ErrorRose
                    VpnStatus.DISCONNECTED -> TextSecondary
                },
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
                letterSpacing = 1.sp
            )

            if (isConnected) {
                Text(
                    text = formatDuration(durationSeconds),
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }

        // Real-time Speeds & Protocol Pill
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Speed Card
            Card(
                colors = CardDefaults.cardColors(containerColor = CardDark),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceAround
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(text = "DOWNLOAD", color = TextSecondary, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                        Text(text = formatSpeed(downloadSpeed), color = TextPrimary, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    }
                    VerticalDivider(
                        color = BorderDark,
                        modifier = Modifier.height(35.dp)
                    )
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(text = "UPLOAD", color = TextSecondary, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                        Text(text = formatSpeed(uploadSpeed), color = TextPrimary, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Quota & Plan Card
            Card(
                colors = CardDefaults.cardColors(containerColor = CardDark),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "Remaining Quota", color = TextSecondary, fontSize = 12.sp)
                        Text(
                            text = if (profile != null && profile!!.trafficLimitBytes > 0) {
                                formatBytes(profile!!.remainingTrafficBytes ?: 0)
                            } else "Unlimited",
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp
                        )
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = {
                            if (profile != null && profile!!.trafficLimitBytes > 0) {
                                (profile!!.usedTrafficBytes.toFloat() / profile!!.trafficLimitBytes.toFloat()).coerceIn(0f, 1f)
                            } else 0f
                        },
                        color = BrandPrimary,
                        trackColor = BorderDark,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(6.dp)
                            .clip(RoundedCornerShape(3.dp))
                    )
                }
            }

            // Protocol Selector Button
            Card(
                colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onNavigateProtocols() }
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Icon(Icons.Default.Security, contentDescription = null, tint = BrandPrimary)
                        Column {
                            Text(text = "Selected Protocol", color = TextSecondary, fontSize = 11.sp)
                            Text(
                                text = viewModel.repository.selectedProtocol.displayName,
                                color = TextPrimary,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 14.sp
                            )
                        }
                    }
                    Icon(Icons.Default.ChevronRight, contentDescription = null, tint = TextSecondary)
                }
            }
        }
    }
}

fun formatSpeed(bytesPerSec: Long): String {
    if (bytesPerSec <= 0) return "0 KB/s"
    val kb = bytesPerSec / 1024
    if (kb < 1024) return "$kb KB/s"
    val mb = kb / 1024.0
    return String.format("%.1f MB/s", mb)
}

fun formatBytes(bytes: Long): String {
    if (bytes <= 0) return "0 B"
    val kb = bytes / 1024.0
    if (kb < 1024) return String.format("%.1f KB", kb)
    val mb = kb / 1024.0
    if (mb < 1024) return String.format("%.1f MB", mb)
    val gb = mb / 1024.0
    return String.format("%.2f GB", gb)
}

fun formatDuration(seconds: Long): String {
    val h = seconds / 3600
    val m = (seconds % 3600) / 60
    val s = seconds % 60
    return if (h > 0) String.format("%02d:%02d:%02d", h, m, s)
    else String.format("%02d:%02d", m, s)
}

