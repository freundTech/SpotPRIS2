use spotify_rs::{
    auth::{AuthFlow, PkceVerifier, Token, Verifier},
    client::Client,
    AuthCodePkceFlow,
};
use zbus::{fdo, interface};

use crate::player::Player;

pub struct MediaPlayer2;

#[interface(name = "org.mpris.MediaPlayer2")]
impl MediaPlayer2 {
    /// Quit method
    async fn quit(&self) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("Not implemented".into()))
    }

    /// Raise method
    async fn raise(&self) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("Not implemented".into()))
    }

    /// CanQuit property
    #[zbus(property)]
    async fn can_quit(&self) -> fdo::Result<bool> {
        Ok(false)
    }

    /// CanRaise property
    #[zbus(property)]
    async fn can_raise(&self) -> fdo::Result<bool> {
        Ok(false)
    }

    /// HasTrackList property
    #[zbus(property)]
    async fn has_track_list(&self) -> fdo::Result<bool> {
        Ok(false)
    }

    /// Identity property
    #[zbus(property)]
    async fn identity(&self) -> fdo::Result<String> {
        Ok("SpotPris2".into())
    }

    /// SupportedMimeTypes property
    #[zbus(property)]
    async fn supported_mime_types(&self) -> fdo::Result<Vec<String>> {
        Ok(vec![])
    }

    /// SupportedUriSchemes property
    #[zbus(property)]
    async fn supported_uri_schemes(&self) -> fdo::Result<Vec<String>> {
        Ok(vec![])
    }
}
