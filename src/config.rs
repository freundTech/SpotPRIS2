use serde::Deserialize;
use std::fs;
use std::path::PathBuf;
use toml;

#[derive(Deserialize)]
pub struct ClientConfig {
    pub client_id: String,
    pub client_secret: String,
}

#[derive(Deserialize)]
pub struct Config {
    pub client: ClientConfig,
}

impl Config {
    pub async fn from_path(path: PathBuf) -> Self {
        let data = fs::read_to_string(path).expect("Unable to read config file");
        let config: Self = toml::from_str(data.as_str()).expect("Malformed config file");

        config
    }
}
