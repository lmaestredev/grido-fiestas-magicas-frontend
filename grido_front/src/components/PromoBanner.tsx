import Image from "next/image";

// Banner image dimensions from Figma
const BANNER_DESKTOP_WIDTH = 1280;
const BANNER_DESKTOP_HEIGHT = 636;
const BANNER_MOBILE_WIDTH = 321;
const BANNER_MOBILE_HEIGHT = 370;

export default function PromoBanner() {
  return (
    <section className="relative w-full overflow-hidden">
      {/* Desktop Banner */}
      <div 
        className="relative w-full hidden md:block"
        style={{ aspectRatio: `${BANNER_DESKTOP_WIDTH}/${BANNER_DESKTOP_HEIGHT}` }}
      >
        <Image
          src="/images/FOOTER-desktop.png"
          alt="Noche Mágica - Traé tu cartita a Papá Noel y llevate 1 helado de regalo. Te esperamos el 18/12, 18hs."
          fill
          className="object-contain object-center scale-[1.002] translate-y-px"
          quality={100}
          sizes="100vw"
        />
      </div>

      {/* Mobile Banner */}
      <div 
        className="relative w-full md:hidden"
        style={{ aspectRatio: `${BANNER_MOBILE_WIDTH}/${BANNER_MOBILE_HEIGHT}` }}
      >
        <Image
          src="/images/footer-banner-mobile.png"
          alt="Noche Mágica - Traé tu cartita a Papá Noel y llevate 1 helado de regalo. Te esperamos el 18/12, 18hs."
          fill
          className="object-contain object-center"
          quality={100}
          sizes="100vw"
        />
      </div>
    </section>
  );
}
