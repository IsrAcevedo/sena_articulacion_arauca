(() => {
    document.addEventListener('DOMContentLoaded', () => {
        
        // 1. Menú hamburguesa
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
            const getScrollAmount = () => {
                const firstCard = carousel.querySelector('.card-item');
                return firstCard ? firstCard.clientWidth + 30 : 350; // Ancho + gap
            };

            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                carousel.scrollBy({ left: -getScrollAmount(), behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                carousel.scrollBy({ left: getScrollAmount(), behavior: 'smooth' });
            });
        }
    });
})();