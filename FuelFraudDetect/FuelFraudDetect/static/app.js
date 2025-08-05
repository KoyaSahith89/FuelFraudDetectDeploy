// Advanced 3D Animations and Interactions for Fuel Fraud Detection App

class FraudDetectionApp {
    constructor() {
        this.isLoading = false;
        this.particles = [];
        this.init();
    }

    init() {
        this.setupPageLoader();
        this.setupFormAnimations();
        this.setupParticleSystem();
        this.setupScrollAnimations();
        this.setupCounterAnimations();
        this.setupInteractiveElements();
        this.setupThemeAnimations();
    }

    // Page Loading Animation
    setupPageLoader() {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const loader = document.querySelector('.page-loader');
                if (loader) {
                    loader.classList.add('hidden');
                    setTimeout(() => loader.remove(), 500);
                }
                this.animatePageEntrance();
            }, 1000);
        });
    }

    animatePageEntrance() {
        // Staggered animation for page elements
        const elements = document.querySelectorAll('.card, .navbar, .alert');
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px) rotateX(15deg)';
            
            setTimeout(() => {
                el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0) rotateX(0)';
            }, index * 100);
        });
    }

    // Enhanced Form Animations
    setupFormAnimations() {
        const form = document.querySelector('form');
        if (!form) return;

        // Input focus animations
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('focus', (e) => {
                this.animateInputFocus(e.target);
            });

            input.addEventListener('blur', (e) => {
                this.animateInputBlur(e.target);
            });

            // Real-time validation animation
            input.addEventListener('input', (e) => {
                this.validateInputRealTime(e.target);
            });
        });

        // Enhanced form submission
        form.addEventListener('submit', (e) => {
            this.handleFormSubmission(e);
        });
    }

    animateInputFocus(input) {
        input.style.transform = 'translateZ(10px) scale(1.02)';
        input.style.boxShadow = '0 8px 25px rgba(13, 110, 253, 0.3)';
        
        // Create floating label effect
        const label = input.parentElement.querySelector('.form-label');
        if (label) {
            label.style.transform = 'translateY(-5px) scale(0.9)';
            label.style.color = '#0d6efd';
        }
    }

    animateInputBlur(input) {
        input.style.transform = 'translateZ(0) scale(1)';
        input.style.boxShadow = '';
        
        const label = input.parentElement.querySelector('.form-label');
        if (label && !input.value) {
            label.style.transform = 'translateY(0) scale(1)';
            label.style.color = '';
        }
    }

    validateInputRealTime(input) {
        const value = parseFloat(input.value);
        const inputName = input.name;
        
        // Remove previous validation classes
        input.classList.remove('is-valid', 'is-invalid', 'warning');
        
        if (value > 0) {
            // Check for potential fraud indicators
            if (inputName === 'fuel_qty' && value > 100) {
                this.addValidationState(input, 'warning', 'High quantity - verify accuracy');
            } else if (inputName === 'rate' && (value < 1.0 || value > 3.0)) {
                this.addValidationState(input, 'warning', 'Unusual rate detected');
            } else if (inputName === 'amount') {
                const fuelQty = document.querySelector('[name="fuel_qty"]').value;
                const rate = document.querySelector('[name="rate"]').value;
                if (fuelQty && rate) {
                    const expected = fuelQty * rate;
                    const deviation = Math.abs(value - expected) / expected;
                    if (deviation > 0.2) {
                        this.addValidationState(input, 'warning', `Expected ~$${expected.toFixed(2)}`);
                    } else {
                        this.addValidationState(input, 'valid', 'Amount looks correct');
                    }
                }
            } else {
                input.classList.add('is-valid');
            }
        }
    }

    addValidationState(input, state, message) {
        input.classList.add(`is-${state}`);
        
        // Add tooltip
        let tooltip = input.parentElement.querySelector('.validation-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.className = 'validation-tooltip';
            input.parentElement.appendChild(tooltip);
        }
        tooltip.textContent = message;
        tooltip.className = `validation-tooltip ${state}`;
    }

    handleFormSubmission(e) {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        // Prevent multiple submissions
        if (this.isLoading) {
            e.preventDefault();
            return;
        }

        this.isLoading = true;
        
        // Animate button loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Add 3D loading animation to form
        const formContainer = e.target.closest('.card');
        if (formContainer) {
            formContainer.style.transform = 'rotateX(5deg) translateZ(10px)';
            formContainer.style.filter = 'blur(1px)';
        }

        // Reset loading state after form processes
        setTimeout(() => {
            this.isLoading = false;
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            if (formContainer) {
                formContainer.style.transform = '';
                formContainer.style.filter = '';
            }
        }, 2000);
    }

    // Particle System for Background
    setupParticleSystem() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        `;
        document.body.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        this.resizeCanvas(canvas);
        
        // Create particles
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                z: Math.random() * 1000,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                vz: Math.random() * 2 + 1,
                size: Math.random() * 3 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }

        // Animate particles
        const animateParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            this.particles.forEach(particle => {
                // Update position
                particle.x += particle.vx;
                particle.y += particle.vy;
                particle.z -= particle.vz;
                
                // Reset particle if it goes off screen
                if (particle.z <= 0) {
                    particle.z = 1000;
                    particle.x = Math.random() * canvas.width;
                    particle.y = Math.random() * canvas.height;
                }
                
                // 3D projection
                const scale = 500 / particle.z;
                const x2d = particle.x * scale + canvas.width / 2;
                const y2d = particle.y * scale + canvas.height / 2;
                const size2d = particle.size * scale;
                
                // Draw particle
                ctx.globalAlpha = particle.opacity * scale;
                ctx.fillStyle = '#0d6efd';
                ctx.beginPath();
                ctx.arc(x2d, y2d, size2d, 0, Math.PI * 2);
                ctx.fill();
            });
            
            requestAnimationFrame(animateParticles);
        };
        
        animateParticles();
        
        window.addEventListener('resize', () => this.resizeCanvas(canvas));
    }

    resizeCanvas(canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    // Scroll-based Animations
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElementInView(entry.target);
                }
            });
        }, observerOptions);

        // Observe cards and other elements
        document.querySelectorAll('.card, .alert, .table-responsive').forEach(el => {
            observer.observe(el);
        });
    }

    animateElementInView(element) {
        element.style.transform = 'translateY(0) rotateX(0) translateZ(0)';
        element.style.opacity = '1';
        
        // Special animations for different element types
        if (element.classList.contains('alert-danger')) {
            element.style.animation = 'fraudAlert 2s ease-in-out';
        } else if (element.classList.contains('alert-success')) {
            element.style.animation = 'successGlow 2s ease-in-out';
        }
    }

    // Counter Animations for Statistics
    setupCounterAnimations() {
        const counters = document.querySelectorAll('[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count) || parseInt(counter.textContent);
            const duration = 2000;
            const start = performance.now();
            
            const animate = (currentTime) => {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                const current = Math.floor(target * easeOutQuart);
                
                counter.textContent = current;
                
                // Add 3D rotation during counting
                const rotation = (1 - progress) * 360;
                counter.style.transform = `rotateY(${rotation}deg)`;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    counter.style.transform = '';
                }
            };
            
            // Start animation when element is visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        requestAnimationFrame(animate);
                        observer.unobserve(counter);
                    }
                });
            });
            
            observer.observe(counter);
        });
    }

    // Interactive Element Enhancements
    setupInteractiveElements() {
        // Enhanced button interactions
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e);
            });
            
            btn.addEventListener('click', (e) => {
                this.createClickEffect(e);
            });
        });

        // Card tilt effect
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                this.handleCardTilt(e, card);
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });

        // Alert interactions
        this.setupAlertAnimations();
    }

    createRippleEffect(e) {
        const button = e.target;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    createClickEffect(e) {
        const button = e.target;
        button.style.transform = 'scale(0.95) rotateX(5deg)';
        
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }

    handleCardTilt(e, card) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
    }

    setupAlertAnimations() {
        document.querySelectorAll('.alert').forEach(alert => {
            // Add entrance animation
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100px) rotateY(45deg)';
            
            setTimeout(() => {
                alert.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                alert.style.opacity = '1';
                alert.style.transform = 'translateX(0) rotateY(0)';
            }, 100);
            
            // Close button animation
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    alert.style.transform = 'translateX(100px) rotateY(45deg) scale(0.8)';
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 500);
                });
            }
        });
    }

    // Theme-based Animations
    setupThemeAnimations() {
        // Create floating elements for atmosphere
        const createFloatingElement = (type) => {
            const element = document.createElement('div');
            element.className = `floating-${type}`;
            element.style.cssText = `
                position: fixed;
                width: ${Math.random() * 20 + 10}px;
                height: ${Math.random() * 20 + 10}px;
                background: ${type === 'fuel' ? '#0d6efd' : '#198754'};
                border-radius: 50%;
                opacity: 0.1;
                pointer-events: none;
                z-index: -1;
                animation: floatAcross ${Math.random() * 10 + 10}s linear infinite;
            `;
            
            element.style.left = '-50px';
            element.style.top = Math.random() * window.innerHeight + 'px';
            
            document.body.appendChild(element);
            
            setTimeout(() => element.remove(), 20000);
        };
        
        // Create floating elements periodically
        setInterval(() => {
            if (Math.random() < 0.3) {
                createFloatingElement(Math.random() < 0.5 ? 'fuel' : 'success');
            }
        }, 2000);
    }
}

// CSS for dynamic animations
const dynamicStyles = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

@keyframes floatAcross {
    from {
        transform: translateX(-50px) translateY(0px) rotate(0deg);
    }
    to {
        transform: translateX(calc(100vw + 50px)) translateY(-100px) rotate(360deg);
    }
}

.validation-tooltip {
    position: absolute;
    bottom: -25px;
    left: 0;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 4px;
    opacity: 0.9;
    animation: slideInUp3D 0.3s ease-out;
}

.validation-tooltip.valid {
    background: rgba(25, 135, 84, 0.9);
    color: white;
}

.validation-tooltip.warning {
    background: rgba(255, 193, 7, 0.9);
    color: black;
}

.form-control.is-valid {
    border-color: #198754;
    box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
}

.form-control.is-warning {
    border-color: #ffc107;
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
}
`;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add dynamic styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = dynamicStyles;
    document.head.appendChild(styleSheet);
    
    // Add page loader
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="loader-3d"></div>';
    document.body.prepend(loader);
    
    // Initialize the app
    window.fraudApp = new FraudDetectionApp();
});

// Export for use in other modules
window.FraudDetectionApp = FraudDetectionApp;