package com.routerlink.app

import com.routerlink.app.data.model.VpnProtocol
import com.routerlink.app.data.model.VpnStatus
import com.routerlink.app.ui.screens.formatBytes
import com.routerlink.app.ui.screens.formatDuration
import com.routerlink.app.ui.screens.formatSpeed
import org.junit.Assert.*
import org.junit.Test

class RouterLinkUnitTest {

    @Test
    fun testProtocolDefaults() {
        assertEquals("openvpn_tcp", VpnProtocol.OPENVPN_TCP.id)
        assertEquals(8443, VpnProtocol.OPENVPN_TCP.port)

        assertEquals("wireguard", VpnProtocol.WIREGUARD.id)
        assertEquals(51820, VpnProtocol.WIREGUARD.port)
    }

    @Test
    fun testFormatBytes() {
        assertEquals("0 B", formatBytes(0))
        assertTrue(formatBytes(1024 * 1024).contains("1.0 MB") || formatBytes(1024 * 1024).contains("1 MB"))
        assertTrue(formatBytes(5L * 1024 * 1024 * 1024).contains("5.00 GB"))
    }

    @Test
    fun testFormatDuration() {
        assertEquals("00:00", formatDuration(0))
        assertEquals("01:05", formatDuration(65))
        assertEquals("01:01:01", formatDuration(3661))
    }

    @Test
    fun testFormatSpeed() {
        assertEquals("0 KB/s", formatSpeed(0))
        assertEquals("500 KB/s", formatSpeed(500 * 1024))
        assertEquals("2.0 MB/s", formatSpeed(2 * 1024 * 1024))
    }

    @Test
    fun testVpnStatusEnum() {
        val statuses = VpnStatus.values()
        assertTrue(statuses.contains(VpnStatus.CONNECTED))
        assertTrue(statuses.contains(VpnStatus.DISCONNECTED))
        assertTrue(statuses.contains(VpnStatus.CONNECTING))
    }
}

