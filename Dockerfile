FROM docker.io/library/python:3.11 AS builder
WORKDIR /app
COPY . .
RUN make

FROM scratch
COPY --chmod=755 --from=builder /app/dist/gpt /usr/local/bin/gpt
ENTRYPOINT ["/usr/local/bin/gpt"]
