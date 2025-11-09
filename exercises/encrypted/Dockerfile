FROM nilcons/debian AS source
RUN mkdir -p /app
COPY key /app/key
FROM scratch
COPY --from=source / /
CMD [ "age", "-i", "/app/key", "-d", "/home/ubuntu/Documents/message.txt" ]
