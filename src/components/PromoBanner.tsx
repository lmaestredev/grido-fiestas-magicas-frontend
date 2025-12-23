import Image from "next/image";

const BANNER_DESKTOP_WIDTH = 1280;
const BANNER_DESKTOP_HEIGHT = 636;
const BANNER_MOBILE_WIDTH = 321;
const BANNER_MOBILE_HEIGHT = 370;

export default function PromoBanner() {
  return (
    <section className="relative w-full overflow-hidden">
      <div 
        className="relative w-full hidden md:block"
        style={{ aspectRatio: `${BANNER_DESKTOP_WIDTH}/${BANNER_DESKTOP_HEIGHT}` }}
      >
        <Image
          src="/images/FOOTER-new-desktop.webp"
          alt="Noche Mágica - Traé tu cartita a Papá Noel y llevate 1 helado de regalo. Te esperamos el 18/12, 18hs."
          fill
          priority
          className="object-contain object-center scale-[1.002] translate-y-px"
          quality={100}
          sizes="(min-width: 768px) 100vw, 0px"
        />
      </div>

      <div 
        className="relative w-full md:hidden"
        style={{ aspectRatio: `${BANNER_MOBILE_WIDTH}/${BANNER_MOBILE_HEIGHT}` }}
      >
        <Image
          src="/images/FOOTER-new-mobile.webp"
          alt="Noche Mágica - Traé tu cartita a Papá Noel y llevate 1 helado de regalo. Te esperamos el 18/12, 18hs."
          fill
          priority
          className="object-contain object-center"
          quality={100}
          sizes="(max-width: 767px) 100vw, 0px"
        />
      </div>
    </section>
  );
}
