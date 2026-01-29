import { useRef, useEffect } from 'react';

interface AdfitProps {
  unit: string;
  width: number;
  height: number;
}

export const Adfit = ({ unit, width, height }: AdfitProps) => {
  const scriptElement = useRef(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.setAttribute('src', 'https://t1.daumcdn.net/kas/static/ba.min.js');
    script.setAttribute('charset', 'utf-8');
    scriptElement.current?.appendChild(script);

    return () => {
      const globalAdfit = window?.adfit;
      if (globalAdfit) globalAdfit.destroy(unit);
    };
  }, []);

  return (
    <div ref={scriptElement}>
      <ins
        className="kakao_ad_area"
        style={{ display: 'none' }}
        data-ad-unit={unit}
        data-ad-width={width}
        data-ad-height={height}
      ></ins>
    </div>
  );
};

export default Adfit;
