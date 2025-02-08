import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.net.Socket;
import java.net.ConnectException;
import java.net.NoRouteToHostException;
import java.net.SocketTimeoutException;

public class TcpScanTest {

    @Test
    void testScanTcp_OpenPort() {
        // This test requires a service running on localhost:8080.  You'll need
        // to have something listening on this port for the test to pass.  For
        // example, you could run a simple web server.
        String result = TcpScan.scan_tcp("localhost", 8080); // Replace with a known open port

        // Check if the result indicates the port is open.  We are being a bit
        // lenient here as the exact format might vary slightly.
        assertTrue(result.contains("abierto"));
    }

    @Test
    void testScanTcp_ClosedPort() {
        String result = TcpScan.scan_tcp("localhost", 8081); // Replace with a known closed port

        // Similar to the open port test, check if the result indicates the port is closed.
        assertTrue(result.contains("cerrado"));
    }

    @Test
    void testScanTcp_InvalidHost() {
        String result = TcpScan.scan_tcp("invalid_host_name", 80);
        assertTrue(result.contains("Error")); // Or a more specific error message check.
    }

    @Test
    void testScanTcp_ConnectionRefused() {
      try {
        // Attempting to connect to a non-existent service on a valid host
        String result = TcpScan.scan_tcp("localhost", 1); // Port likely to be unused
        assertTrue(result.contains("cerrado") || result.contains("Error")); // Check for closed or error
      } catch (Exception e) {
        fail("Should not throw an exception: " + e.getMessage());
      }
    }

    @Test
    void testScanTcp_Timeout() {
        // For this test, you might want to try connecting to a host that is
        // unreachable from your network.  This will cause a timeout.
        String result = TcpScan.scan_tcp("192.168.2.1", 80); // Example private IP, might not work for everyone
        assertTrue(result.contains("Error") || result.contains("cerrado")); // Timeout is often reported as closed
    }

    public static void main(String[] args) {
        org.junit.runner.JUnitCore.main("TcpScanTest");
    }
}


// TcpScan.java (The Java equivalent of your Python code)
import java.net.Socket;
import java.net.ConnectException;
import java.net.NoRouteToHostException;
import java.net.SocketTimeoutException;
import java.io.IOException;

public class TcpScan {

    public static String scan_tcp(String host, int port) {
        try (Socket sock = new Socket()) { // Try-with-resources for auto-closing
            sock.setSoTimeout(1000); // 1-second timeout
            try {
                sock.connect(new java.net.InetSocketAddress(host, port), 1000);
                return String.format("Puerto TCP %d abierto", port);
            } catch (ConnectException | NoRouteToHostException | SocketTimeoutException ex) {
                return String.format("Puerto TCP %d cerrado", port);
            } catch (IOException e) {
                return String.format("Error en el puerto TCP %d: %s", port, e.getMessage());
            }

        } catch (IOException e) {
            return String.format("Error al crear socket: %s", e.getMessage());
        }
    }
}