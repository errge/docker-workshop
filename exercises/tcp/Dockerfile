FROM nilcons/debian AS build
RUN apt-get update && apt-get install -y musl-tools binutils && mkdir -p /app
COPY main.c /app
RUN musl-gcc -static -Os -o /app/main /app/main.c
CMD [ "/app/main" ]
FROM scratch
COPY --from=nilcons/debian / /
COPY --from=build /app/main /main
CMD [ "/main" ]
