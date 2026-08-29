(() => {
    document.addEventListener('DOMContentLoaded', () => {
        
        // 1. Menú hamburguesa (con validación de existencia)
        const menuToggle = document.getElementById('menu-toggle');
        const menu = document.getElementById('menu');

        if (menuToggle && menu) {
            menuToggle.addEventListener('click', (e) => {
                e.preventDefault();
                menu.classList.toggle('show');
            });
        }

        // 2. Carrusel de municipios
        const carousel = document.getElementById('municipiosCarousel');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (carousel && prevBtn && nextBtn) {
            
            // Función para calcular dinámicamente el desplazamiento por tarjeta
            const getScrollAmount = () => {
                const firstCard = carousel.querySelector('.card-item');
                return firstCard ? firstCard.clientWidth + 30 : 340;
            };

            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                carousel.scrollBy({ left: -getScrollAmount(), behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                carousel.scrollBy({ left: getScrollAmount(), behavior: 'smooth' });
            });
        }
        
    });
})();