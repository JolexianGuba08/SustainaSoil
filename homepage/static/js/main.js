gsap.from([".navbar img", ".navbar h1"], {
    duration: 1,
    xPercent: -100,
    opacity: 0
});

gsap.from([".sign-in", ".sign-up"], {
    duration: 2,
    xPercent: 1,
    opacity: 0
});

gsap.from(".aside-container", {
    duration: 2,
    xPercent: -30,
    opacity: -2
});