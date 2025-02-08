import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;

public class UdpScanTest {

    @Test
    void testScanUdp_OpenOrFilteredPort() throws IOException {
        // UDP is connectionless.  A successful send does NOT mean the port is open.
        // It could also mean there is no service listening, but the port is not
        // blocked by a firewall.  A timeout is the typical result.
        String result = UdpScan.scan_udp("localhost", 53); // Replace with a known port (e.g., DNS) or unlikely port

        // Because of the nature of UDP, a timeout (which means filtered)
        // is the most likely result.  However, if a service responds very
        // quickly, it might be considered open.  We will accept either.
        assertTrue(result.contains("filtrado") || result.contains("abierto"));
    }


    @Test
    void testScanUdp_InvalidHost() {
        String result = UdpScan.scan_udp("invalid_host_name", 53);
        assertTrue(result.contains("Error"));
    }

    @Test
    void testScanUdp_NoRouteToHost() {
      String result = UdpScan.scan_udp("192.168.2.1", 53); // Likely unreachable
      assertTrue(result.contains("Error") || result.contains("filtrado")); // Expect error or filtered
    }


    public static void main(String[] args) {
        org.junit.runner.JUnitCore.main("UdpScanTest");
    }
}

// UdpScan.java (Java equivalent of your Python code)
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;

public class UdpScan {

    public static String scan_udp(String host, int port) {
        try (DatagramSocket sock = new DatagramSocket()) {
            sock.setSoTimeout(1000); // 1-second timeout

            try {
                InetAddress addr = InetAddress.getByName(host);
                byte[] buffer = new byte[0]; // Empty byte array for UDP send
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length, addr, port);
                sock.send(packet);

                // Try to receive a response (this is what distinguishes open from filtered)
                byte[] recvBuf = new byte[1024];
                DatagramPacket recvPacket = new DatagramPacket(recvBuf, recvBuf.length);
                sock.receive(recvPacket);

                return String.format("Puerto UDP %d abierto", port);

            } catch (SocketTimeoutException ex) {
                return String.format("Puerto UDP %d filtrado", port);
            } catch (IOException e) {
                return String.format("Error en el puerto UDP %d: %s", port, e.getMessage());
            }

        } catch (IOException e) {
            return String.format("Error al crear socket: %s", e.getMessage());
        }
    }
}