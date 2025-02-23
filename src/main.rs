mod config;
mod error;
mod media_player2;
mod player;

use axum::{
    extract::{Query, State},
    routing::get,
    Router,
};
use config::Config;
use dirs;
use media_player2::MediaPlayer2;
use player::Player;
use serde::Deserialize;
use spotify_rs::{
    auth::{NoVerifier, Token},
    client::Client,
    AuthCodePkceClient, AuthCodePkceFlow, RedirectUrl,
};
use std::sync::Arc;
use tokio::sync::broadcast;
use tokio::sync::broadcast::{Receiver, Sender};
use zbus::connection;

const CLIENT_ID: &'static str = "58e60c00289940d39bc2f3bf477abad8";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut path = dirs::config_dir().unwrap();
    path.push("spotpris2.toml");
    let config = Config::from_path(path).await;
    let spotify = authenticate(&config).await.unwrap();

    let _connection = connection::Builder::session()?
        .name("org.mpris.MediaPlayer2.spotpris2")?
        .serve_at("/org/mpris/MediaPlayer2", MediaPlayer2)?
        .serve_at("/org/mpris/MediaPlayer2", Player::new(spotify))?
        .build()
        .await?;

    loop {}
}

async fn authenticate(
    config: &Config,
) -> Result<Client<Token, AuthCodePkceFlow, NoVerifier>, Box<dyn std::error::Error>> {
    let redirect_url = RedirectUrl::new("http://localhost:8000".to_owned()).unwrap();
    let auto_refresh = true;
    let scopes = vec![
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    ];
    let auth_code_flow = AuthCodePkceFlow::new(CLIENT_ID, scopes);
    let (client, url) = AuthCodePkceClient::new(auth_code_flow, redirect_url, auto_refresh);

    let (tx, mut rx): (Sender<OAuthResponse>, Receiver<OAuthResponse>) = broadcast::channel(1);
    let mut rx2 = tx.subscribe();

    webbrowser::open(url.as_str()).unwrap();

    let webserver = Router::new().route("/", get(move |body| finish_auth(body, tx)));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8000")
        .await
        .unwrap();
    axum::serve(listener, webserver)
        .with_graceful_shutdown(async move {
            let mut res = rx2.recv().await;
            while let Err(_) = res {
                res = rx2.recv().await;
            }
        })
        .await
        .unwrap();

    let response = rx.recv().await.unwrap();

    let mut spotify = client.authenticate(response.code, response.state).await?;
    println!("Authenticated");

    Ok(spotify)
}

#[derive(Deserialize, Clone, Debug)]
struct OAuthResponse {
    code: String,
    state: String,
}

async fn finish_auth(
    Query(response): Query<OAuthResponse>,
    state: Sender<OAuthResponse>,
) -> &'static str {
    state.send(response).unwrap();

    "Authentication successful."
}
