import { useEffect, useRef, useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Pin,
  useMap,
} from "@vis.gl/react-google-maps";

import { locations } from "./locations";
function CenterOnUser({ position }) {
  const map = useMap();
  const hasCentered = useRef(false);

  useEffect(() => {
    if (!map || !position || hasCentered.current) {
      return;
    }

    map.panTo(position);
    map.setZoom(15);
    hasCentered.current = true;
  }, [map, position]);

  return null;
}

export default function MapView() {
  const [selectedLocation, setSelectedLocation] = useState(null);
//   const [zoom, setZoom] = useState(12);

//   const pinScale = Math.max(0.01, Math.min(1, zoom / 12));

    const [userLocation, setUserLocation] = useState(null);
    const [locationError, setLocationError] = useState("");

    useEffect(() => {
    if (!navigator.geolocation) {
        setLocationError("Location is not supported by this browser.");
        return;
    }

    const watchId = navigator.geolocation.watchPosition(
        (position) => {
        setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
        });

        setLocationError("");
        },
        (error) => {
        setLocationError(error.message);
        },
        {
        enableHighAccuracy: true,
        maximumAge: 5000,
        timeout: 10000,
        },
    );

    return () => navigator.geolocation.clearWatch(watchId);
    }, []);

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
        <CenterOnUser position={userLocation} />
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
                background="rgb(194, 66, 73)"
                borderColor="rgb(144, 21, 27)"
                glyphColor="rgb(255, 202, 244)"
                // scale={pinScale}
            />
            </AdvancedMarker>
        ))}

        {userLocation && (
            <AdvancedMarker
                position={userLocation}
                title="Your current location"
                zIndex={1000}
            >
                <Pin
                background="rgb(82, 127, 198)"
                borderColor="rgb(35, 80, 152)"
                glyphColor="rgb(160, 188, 232)"
                scale={1.2}
                />
            </AdvancedMarker>
            )}

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
                {/* <div style={{ marginTop: "6px" }}>
                    {selectedLocation.name}
                </div> */}
                <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${selectedLocation.lat},${selectedLocation.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ display: "inline-block", marginTop: "10px" }}
                >
                    {selectedLocation.name}
                </a>
                </div>
            </InfoWindow>
            )}
      </Map>
    </APIProvider>
  );
}