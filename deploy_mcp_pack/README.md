# Deploy mcp_pack

Users shouldn't need to do this -- this is just for developers to start their own server.

To start the server, run `deploy`.

To monitor:
- Check logs: `tail -f starsim.log`
- Check if running: `ps -p $(cat server_pids.txt | cut -d: -f2)`
- Stop servers: `kill $(cat server_pids.txt | cut -d: -f2)`
