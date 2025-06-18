function setupDownloadButtons() {
    const downloadUrls = {
        'orion': 'http://start.orionstars.vip:8580/index.html',
        'firekirin': 'http://start.firekirin.xyz:8580/index.html',
        'juwa': 'https://dl.juwa777.com',
        'ultrapanda': 'https://www.ultrapanda.mobi/',
        'pandamaster': 'https://pandamaster.com',
        'vegas': 'https://m.lasvegassweeps.com/',
        'gamevault': 'https://download.gamevault999.com/',
        'vblink': 'https://vblink.net/'
    };

    document.querySelectorAll('.btn-download').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const game = this.dataset.game;
            window.open(downloadUrls[game] || '#', '_blank');
        });
    });
}

document.addEventListener('DOMContentLoaded', setupDownloadButtons);
