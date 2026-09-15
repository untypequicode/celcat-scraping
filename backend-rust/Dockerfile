# Étape 1 : Construction
FROM rust:1-slim-bookworm AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Compile l'application en mode release optimisé
RUN cargo build --release

# Étape 2 : Image finale (très légère)
FROM debian:bookworm-slim

WORKDIR /app

# Installation des certificats SSL nécessaires pour HTTPS
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/celcat-to-ics /app/celcat-to-ics

# L'utilisateur non-root pour la sécurité
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["./celcat-to-ics"]
