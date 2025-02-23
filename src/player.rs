use serde::{Deserialize, Serialize};
use spotify_rs::{
    auth::{AuthFlow, Authorised, Token, Verifier},
    client::Client,
    model::{player::PlaybackState, PlayableItem},
};
use std::collections::HashMap;
use zbus::{
    fdo, interface,
    zvariant::{self, OwnedValue, Str, Type, Value},
};

use crate::media_player2::{self, MediaPlayer2};

#[derive(Serialize, Deserialize, Type)]
#[zvariant(signature = "s")]
pub enum LoopStatus {
    None,
    Track,
    Playlist,
}

impl TryFrom<Value<'_>> for LoopStatus {
    type Error = zvariant::Error;

    fn try_from(value: Value<'_>) -> Result<Self, zvariant::Error> {
        if let Value::Str(string) = value {
            match string.as_str() {
                "None" => Ok(LoopStatus::None),
                "Track" => Ok(LoopStatus::Track),
                "Playlist" => Ok(LoopStatus::Playlist),
                _ => Err(zvariant::Error::Message(
                    "Value must be one of None, Track, or Playlist".into(),
                )),
            }
        } else {
            Err(zvariant::Error::IncorrectType)
        }
    }
}

impl From<LoopStatus> for Value<'static> {
    fn from(status: LoopStatus) -> Value<'static> {
        Value::from(match status {
            LoopStatus::None => "None",
            LoopStatus::Track => "Track",
            LoopStatus::Playlist => "Playlist",
        })
    }
}

#[derive(Serialize, Deserialize, Type)]
#[zvariant(signature = "s")]
pub enum PlaybackStatus {
    Playing,
    Paused,
    Stopped,
}

impl TryFrom<Value<'_>> for PlaybackStatus {
    type Error = zvariant::Error;

    fn try_from(value: Value<'_>) -> Result<Self, zvariant::Error> {
        if let Value::Str(string) = value {
            match string.as_str() {
                "Playing" => Ok(PlaybackStatus::Playing),
                "Paused" => Ok(PlaybackStatus::Paused),
                "Stopped" => Ok(PlaybackStatus::Stopped),
                _ => Err(zvariant::Error::Message(
                    "Value must be one of Playing, Paused, or Stopped".into(),
                )),
            }
        } else {
            Err(zvariant::Error::IncorrectType)
        }
    }
}

impl From<PlaybackStatus> for Value<'static> {
    fn from(status: PlaybackStatus) -> Value<'static> {
        Value::from(match status {
            PlaybackStatus::Playing => "Playing",
            PlaybackStatus::Paused => "Paused",
            PlaybackStatus::Stopped => "Stopped",
        })
    }
}

pub struct Player<F: AuthFlow + Authorised, V: Verifier> {
    spotify: Client<Token, F, V>,
    playback_state: Option<PlaybackState>,
}

impl<F: AuthFlow + Authorised, V: Verifier> Player<F, V> {
    pub fn new(spotify: Client<Token, F, V>) -> Self {
        Self {
            spotify,
            playback_state: Option::None,
        }
    }

    pub async fn update(&mut self) {
        let old_playback_state = self.playback_state.clone();
        self.playback_state = self
            .spotify
            .get_currently_playing_track(Option::None)
            .await
            .ok();
    }
}

#[interface(name = "org.mpris.MediaPlayer2.Player")]
impl<F: AuthFlow + Authorised + Sync + Send + 'static, V: Verifier + Sync + Send + 'static>
    Player<F, V>
{
    /// Next method
    async fn next(&mut self) -> fdo::Result<()> {
        match self.spotify.skip_to_next(Option::None).await {
            Ok(_) => Ok(()),
            Err(_) => Err(fdo::Error::Failed("Request failed".into())),
        }
    }

    /// OpenUri method
    async fn open_uri(&self, arg_1: &str) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("Not implemented".into()))
    }

    /// Pause method
    async fn pause(&mut self) -> fdo::Result<()> {
        match self.spotify.pause_playback(Option::None).await {
            Ok(_) => Ok(()),
            Err(_) => Err(fdo::Error::Failed("Request failed".into())),
        }
    }

    /// Play method
    async fn play(&mut self) -> fdo::Result<()> {
        match self.spotify.start_playback().send().await {
            Ok(_) => Ok(()),
            Err(_) => Err(fdo::Error::Failed("Request failed".into())),
        }
    }

    /// PlayPause method
    async fn play_pause(&mut self) -> fdo::Result<()> {
        if let Some(state) = &self.playback_state {
            if state.is_playing {
                self.pause().await
            } else {
                self.play().await
            }
        } else {
            Err(fdo::Error::Failed("No song selected".into()))
        }
    }

    /// Previous method
    async fn previous(&mut self) -> fdo::Result<()> {
        match self.spotify.skip_to_previous(Option::None).await {
            Ok(_) => Ok(()),
            Err(_) => Err(fdo::Error::Failed("Request failed".into())),
        }
    }

    /// Seek method
    async fn seek(&self, Offset: i64) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// SetPosition method
    async fn set_position(
        &self,
        TrackId: zbus::zvariant::ObjectPath<'_>,
        Position: i64,
    ) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// Stop method
    async fn stop(&self) -> fdo::Result<()> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// Seeked signal
    /*
    #[zbus(signal)]
    async fn seeked(emitter: &SignalEmitter<'_>, Position: i64) -> zbus::Result<()>;
    */

    /// CanControl property
    #[zbus(property)]
    async fn can_control(&self) -> fdo::Result<bool> {
        Ok(false)
    }

    /// CanGoNext property
    #[zbus(property)]
    async fn can_go_next(&self) -> fdo::Result<bool> {
        Ok(true)
    }

    /// CanGoPrevious property
    #[zbus(property)]
    async fn can_go_previous(&self) -> fdo::Result<bool> {
        Ok(true)
    }

    /// CanPause property
    #[zbus(property)]
    async fn can_pause(&self) -> fdo::Result<bool> {
        Ok(true)
    }

    /// CanPlay property
    #[zbus(property)]
    async fn can_play(&self) -> fdo::Result<bool> {
        Ok(true)
    }

    /// CanSeek property
    #[zbus(property)]
    async fn can_seek(&self) -> fdo::Result<bool> {
        Ok(false)
    }

    /// LoopStatus property
    #[zbus(property)]
    async fn loop_status(&self) -> fdo::Result<LoopStatus> {
        Ok(LoopStatus::Playlist)
    }
    #[zbus(property)]
    async fn set_loop_status(&self, value: LoopStatus) -> zbus::Result<()> {
        Err(zbus::Error::Unsupported)
    }

    /// MaximumRate property
    #[zbus(property)]
    async fn maximum_rate(&self) -> fdo::Result<f64> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// Metadata property
    #[zbus(property)]
    async fn metadata(&self) -> fdo::Result<HashMap<String, zvariant::OwnedValue>> {
        let mut metadata: HashMap<String, zvariant::OwnedValue> = HashMap::new();
        metadata.insert(
            "xesam:trackid".into(),
            OwnedValue::from(zvariant::Str::from_static(
                "/com/spotify/track/adkfjaoidfjasdif",
            )),
        );
        metadata.insert(
            "xesam:title".into(),
            OwnedValue::from(Str::from("Test Title")),
        );
        metadata.insert(
            "xesam:artist".into(),
            OwnedValue::from(zvariant::Str::from_static("Test Artist")),
        );

        Ok(metadata)
    }

    /// MinimumRate property
    #[zbus(property)]
    async fn minimum_rate(&self) -> fdo::Result<f64> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// PlaybackStatus property
    #[zbus(property)]
    async fn playback_status(&self) -> fdo::Result<PlaybackStatus> {
        match &self.playback_state {
            Some(state) => Ok(if state.is_playing {
                PlaybackStatus::Playing
            } else if let Option::Some(_) = state.item {
                PlaybackStatus::Paused
            } else {
                PlaybackStatus::Stopped
            }),
            None => Err(fdo::Error::Failed("Failed".into())),
        }
    }

    /// Position property
    #[zbus(property)]
    async fn position(&self) -> fdo::Result<i64> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }

    /// Rate property
    #[zbus(property)]
    async fn rate(&self) -> fdo::Result<f64> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }
    #[zbus(property)]
    async fn set_rate(&self, value: f64) -> zbus::Result<()> {
        Err(zbus::Error::Unsupported)
    }

    /// Shuffle property
    #[zbus(property)]
    async fn shuffle(&self) -> fdo::Result<bool> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }
    #[zbus(property)]
    async fn set_shuffle(&self, value: bool) -> zbus::Result<()> {
        Err(zbus::Error::Unsupported)
    }

    /// Volume property
    #[zbus(property)]
    async fn volume(&self) -> fdo::Result<f64> {
        Err(fdo::Error::NotSupported("NotImplemented".into()))
    }
    #[zbus(property)]
    async fn set_volume(&self, value: f64) -> zbus::Result<()> {
        Err(zbus::Error::Unsupported)
    }
}
