FROM cowrie/cowrie:latest

# Copy custom Cowrie configuration
COPY cowrie.cfg /cowrie/etc/cowrie.cfg
COPY userdb.txt /cowrie/etc/userdb.txt

# Expose SSH (2222) and Telnet (2323)
EXPOSE 2222 2323
