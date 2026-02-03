"use client";

import { useState, useEffect, useRef } from "react";

export function useScrollSpy(ids: string[]) {
  const [activeId, setActiveId] = useState<string>("");
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const options = {
      root: null,
      rootMargin: "-10% 0px -80% 0px",
      threshold: 0,
    };

    const callback: IntersectionObserverCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const newId = entry.target.id;
          setActiveId(newId);
          window.history.replaceState(null, "", `#${newId}`);
        }
      });
    };

    observerRef.current = new IntersectionObserver(callback, options);

    ids.forEach((id) => {
      const element = document.getElementById(id);
      if (element) observerRef.current?.observe(element);
    });

    return () => {
      observerRef.current?.disconnect();
    };
  }, [ids]);

  return activeId;
}
