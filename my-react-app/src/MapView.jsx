import { useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Pin,
} from "@vis.gl/react-google-maps";

import { locations } from "./locations";

export default function MapView() {
  const [selectedLocation, setSelectedLocation] = useState(null);
//   const [zoom, setZoom] = useState(12);

//   const pinScale = Math.max(0.01, Math.min(1, zoom / 12));

  return (
    <APIProvider apiKey={import.meta.env.VITE_GM_API_KEY}>
      <Map
        defaultCenter={{
          lat: -33.8688,
          lng: 151.2093,
        }}
        defaultZoom={12}
        mapId={import.meta.env.VITE_GM_MAP_ID}
        gestureHandling="greedy"
        mapTypeControl={false}
        streetViewControl={false}
        rotateControl={false}
        tiltInteractionEnabled={false}
        fullscreenControl={false}
        zoomControl={false}
        cameraControl={false}
        defaultTilt={0}
        style={{
          width: "100%",
          height: "100%",
        }}
      >
        {locations.map((location) => (
          <AdvancedMarker
            key={location.id}
            position={{
              lat: location.lat,
              lng: location.lng,
            }}
            title={location.name}
            onClick={() => setSelectedLocation(location)}
            >
            <Pin
                background="#cb5480"
                borderColor="#a0355c"
                glyphColor="#ee91b3"
                // scale={pinScale}
            />
            </AdvancedMarker>
        ))}

        {/* {selectedLocation && (
          <InfoWindow
            position={{
              lat: selectedLocation.lat,
              lng: selectedLocation.lng,
            }}
            onCloseClick={() => setSelectedLocation(null)}
          >
            <div>
              <strong>{selectedLocation.name}</strong>

              {selectedLocation.description && (
                <p>{selectedLocation.description}</p>
              )}
            </div>
          </InfoWindow>
        )} */}

        {selectedLocation && (
            <InfoWindow
                key={selectedLocation.id}
                position={{
                lat: selectedLocation.lat,
                lng: selectedLocation.lng,
                }}
                onCloseClick={() => setSelectedLocation(null)}
            >
                <div className="custom-popup">
                <div style={{ fontWeight: 700 }}>
                    {selectedLocation.id}
                </div>

                <div className="custom-popup" style={{ marginTop: "6px" }}>
                    {selectedLocation.name}
                </div>
                </div>
            </InfoWindow>
            )}
      </Map>
    </APIProvider>
  );
}