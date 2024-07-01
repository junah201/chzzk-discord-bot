import { useState, useEffect } from 'react';
import ReactGA from 'react-ga4';
import { useLocation } from 'react-router-dom';

const { VITE_GA_TRACKING_ID } = import.meta.env;

export const RouteChangeTracker = () => {
  const location = useLocation();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!isInitialized) {
      ReactGA.initialize(VITE_GA_TRACKING_ID);
      setIsInitialized(true);
    }
  }, []);

  useEffect(() => {
    if (isInitialized) {
      ReactGA.send({
        hitType: 'pageview',
        page: location.pathname,
      });
    }
  }, [isInitialized, location]);
};

export default RouteChangeTracker;
