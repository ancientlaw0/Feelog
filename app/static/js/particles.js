tsParticles.load("tsparticles", {
  fullScreen: { enable: false },
  background: {
    color: "#f8fbfa" 
  },
  particles: {
    number: {
      value: 100,
      density: { enable: true, area: 800 }
    },
    color: { value: "#5a9289" },
    shape: { type: "circle" },
    opacity: {
      value: 0.6,
      random: false
    },
    size: {
      value: 6,
      random: true
    },
    move: {
      enable: true,
      speed: 0.8,
      direction: "none",
      random: true,
      straight: false,
      outMode: "out"
    },

  },
  interactivity: {
    events: {
      onhover: {
        enable: true,
        mode: "grab"
      },
      onclick: {
        enable: true,
        mode:"repulse"
      },
      resize: true
    },
    modes: {
      grab: {
        distance: 150,
        links: {
          opacity: 0.5
        }
      }
    }
  },
  detectRetina: true
});