FROM nilcons/debian AS source
RUN mkdir -p /app && echo aGVsbG8gZG9ja2VyIHdvcmtzaG9wCg== | base64 --decode >/app/hello.txt
FROM scratch
COPY --from=source / /
CMD [ "/bin/bash" ]
