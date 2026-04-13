import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export const initTryOnYouAnimation = (): void => {
    const tl = gsap.timeline({
        scrollTrigger: {
            trigger: ".macbook-section", // Contenedor principal
            start: "top top",
            end: "+=2000",
            scrub: 1, // Suavizado de la animación
            pin: true,
        },
    });

    // 1. Animación de apertura del MacBook (Ángulo 3D)
    tl.to(".macbook-lid", { rotationX: -110, duration: 2 })

    // 2. Encendido de pantalla con el logo de TryOnYou
      .to(".macbook-screen", { opacity: 1, duration: 1 }, "-=1")

    // 3. Revelación de los 5 Looks Maestros (Efecto GSAP)
      .from(".look-card", {
          y: 100,
          stagger: 0.2,
          opacity: 0,
          ease: "power2.out",
      });

    console.log("🚀 Animación GSAP consolidada: MacBook Ready.");
};
