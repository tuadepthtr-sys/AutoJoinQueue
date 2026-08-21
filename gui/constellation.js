/**
 * Dynamic Constellation & Falling Snowflakes Canvas Engine (High FPS, Low Memory/CPU)
 */
(function() {
    const canvas = document.getElementById('constellationCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let particles = [];
    let snowflakes = [];
    let animationFrameId = null;
    let enabled = true;

    const config = {
        particleCount: 35,
        snowflakeCount: 45,
        maxDistance: 120,
        maxDistanceSq: 120 * 120,
        particleSpeed: 0.35,
        starColors: ['#ffffff', '#a855f7', '#6366f1', '#06b6d4'],
        mouseRadius: 120,
        mouseRadiusSq: 120 * 120
    };

    const mouse = {
        x: null,
        y: null
    };

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.x = Math.random() * (width || 800);
            this.y = Math.random() * (height || 600);
            this.vx = (Math.random() - 0.5) * config.particleSpeed;
            this.vy = (Math.random() - 0.5) * config.particleSpeed;
            this.radius = Math.random() * 1.8 + 1;
            this.color = config.starColors[Math.floor(Math.random() * config.starColors.length)];
            this.alpha = Math.random() * 0.6 + 0.4;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distSq = dx * dx + dy * dy;
                if (distSq < config.mouseRadiusSq && distSq > 0) {
                    const dist = Math.sqrt(distSq);
                    const force = (config.mouseRadius - dist) / config.mouseRadius;
                    this.x -= (dx / dist) * force * 1.2;
                    this.y -= (dy / dist) * force * 1.2;
                }
            }
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    class Snowflake {
        constructor(initialSpawn = true) {
            this.reset(initialSpawn);
        }

        reset(initialSpawn = false) {
            this.x = Math.random() * (width || 800);
            this.y = initialSpawn ? Math.random() * (height || 600) : -10;
            this.vy = Math.random() * 1.2 + 0.5; // Downward fall speed
            this.radius = Math.random() * 2.2 + 0.8; // Snowflake size
            this.alpha = Math.random() * 0.7 + 0.3; // Soft white opacity
            this.swingStep = Math.random() * 0.03 + 0.01; // Horizontal sway frequency
            this.swingAngle = Math.random() * Math.PI * 2;
            this.swingAmplitude = Math.random() * 0.6 + 0.2;
        }

        update() {
            this.y += this.vy;
            this.swingAngle += this.swingStep;
            this.x += Math.sin(this.swingAngle) * this.swingAmplitude;

            if (this.y > height + 10) {
                this.reset(false);
            }
            if (this.x < -10) this.x = width + 10;
            if (this.x > width + 10) this.x = -10;
        }

        draw() {
            ctx.fillStyle = '#ffffff';
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function init() {
        resize();
        particles = [];
        snowflakes = [];
        
        for (let i = 0; i < config.particleCount; i++) {
            particles.push(new Particle());
        }
        for (let i = 0; i < config.snowflakeCount; i++) {
            snowflakes.push(new Snowflake(true));
        }
    }

    function animate() {
        if (!enabled) return;

        ctx.clearRect(0, 0, width, height);

        // Draw Constellation Star Lines
        const len = particles.length;
        for (let i = 0; i < len; i++) {
            const p1 = particles[i];
            p1.update();
            p1.draw();

            for (let j = i + 1; j < len; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distSq = dx * dx + dy * dy;

                if (distSq < config.maxDistanceSq) {
                    const dist = Math.sqrt(distSq);
                    const alpha = (1 - dist / config.maxDistance) * 0.25;
                    ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`;
                    ctx.lineWidth = 0.7;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }

        // Draw Falling White Snowflakes
        const sLen = snowflakes.length;
        for (let i = 0; i < sLen; i++) {
            const flake = snowflakes[i];
            flake.update();
            flake.draw();
        }

        animationFrameId = requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    window.ConstellationEngine = {
        start: function() {
            enabled = true;
            init();
            if (!animationFrameId) animate();
        },
        stop: function() {
            enabled = false;
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            ctx.clearRect(0, 0, width, height);
        },
        toggle: function(state) {
            if (state) this.start();
            else this.stop();
        }
    };

    window.ConstellationEngine.start();
})();
