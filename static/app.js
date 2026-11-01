(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const state = { industry: 'all', category: 'popular', page: 1, query: '', movies: [], live: false, activeView: 'discover', boxOffice: [], loading: false };
  const INDUSTRIES = { all: 'All industries', tollywood: 'Tollywood', bollywood: 'Bollywood', hollywood: 'Hollywood' };
  const CATEGORIES = { popular: 'Popular movies', 'now-playing': 'Recently released', 'top-rated': 'Top rated movies', upcoming: 'Upcoming movies' };
  const LANGUAGES = { te: 'Telugu', hi: 'Hindi', en: 'English' };
  const fmtNum = (n) => Number.isFinite(Number(n)) ? Number(n).toLocaleString('en-IN') : '—';
  const fmtMoney = (n) => {
    if (n === null || n === undefined || n === '' || !Number.isFinite(Number(n)) || Number(n) <= 0) return 'Not reported';
    const v = Number(n);
    if (v >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B';
    if (v >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (v >= 1000) return '$' + (v / 1000).toFixed(0) + 'K';
    return '$' + Math.round(v).toLocaleString('en-US');
  };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  const getMovie = (id) => state.movies.find((m) => String(m.id) === String(id)) || state.boxOffice.find((m) => String(m.id) === String(id));
  let toastTimer;
  function toast(message) { const el = $('#toast'); el.textContent = message; el.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2600); }
  function showNotice(message, type = '') { const el = $('#global-notice'); if (!message) { el.classList.add('hidden'); return; } el.textContent = message; el.className = 'notice' + (type ? ' ' + type : ''); }
<<<<<<< HEAD
  function setStatus(live, text) { const dot = $('.status-dot'); dot.classList.toggle('demo', !live); $('#data-status').textContent = text || (live ? 'Local dataset' : 'Dataset not installed'); }
  function fallbackPoster(movie) { return `<div class="poster-fallback"><span class="fallback-mark">▶</span><span>${esc(movie.industry || 'Cinema')}</span><strong>${esc(movie.title || 'Movie')}</strong></div>`; }
  function renderCard(movie) {
    const poster = movie.poster_url || (movie.poster_path && String(movie.poster_path).startsWith('/') ? '' : '');
    const img = poster ? `<img loading="lazy" src="${esc(poster)}" alt="${esc(movie.title)} poster">` : fallbackPoster(movie);
    const rating = movie.vote_average != null && Number(movie.vote_average) > 0 ? Number(movie.vote_average).toFixed(1) : 'N/A';
    const genre = (movie.genre_names || []).slice(0, 2).map((g) => `<span class="genre-pill">${esc(g)}</span>`).join('');
    return `<article class="movie-card" tabindex="0" role="button" data-movie-id="${esc(movie.id)}" aria-label="View details for ${esc(movie.title)}"><div class="poster-wrap">${img}<span class="industry-badge">${esc(movie.industry || 'Cinema')}</span><span class="rating-badge">${rating === 'N/A' ? 'SAMPLE' : '★ ' + rating}</span></div><div class="movie-meta"><h4 class="movie-title" title="${esc(movie.title)}">${esc(movie.title)}</h4><div class="movie-subtitle"><span>${esc(movie.year || (movie.release_date || '').slice(0, 4) || 'Year N/A')}</span><span>${esc((movie.genre_names || [])[0] || 'Movie')}</span></div><div class="genre-pills">${genre}</div></div></article>`;
=======
  function setStatus(live, text) { const dot = $('.status-dot'); dot.classList.toggle('demo', !live); $('#data-status').textContent = text || (live ? 'TMDB live data' : 'Offline sample mode'); }
  function fallbackPoster(movie) { return `<div class="poster-fallback"><span class="fallback-mark">▶</span><span>${esc(movie.industry || 'Cinema')}</span><strong>${esc(movie.title || 'Movie')}</strong></div>`; }
  function renderCard(movie) {
    const poster = movie.poster_url || (movie.poster_path && String(movie.poster_path).startsWith('/') ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '');
    const img = poster ? `<img loading="lazy" src="${esc(poster)}" alt="${esc(movie.title)} poster">` : fallbackPoster(movie);
    const rating = movie.vote_average != null && Number(movie.vote_average) > 0 ? Number(movie.vote_average).toFixed(1) : 'DEMO';
    const genre = (movie.genre_names || []).slice(0, 2).map((g) => `<span class="genre-pill">${esc(g)}</span>`).join('');
    return `<article class="movie-card" tabindex="0" role="button" data-movie-id="${esc(movie.id)}" aria-label="View details for ${esc(movie.title)}"><div class="poster-wrap">${img}<span class="industry-badge">${esc(movie.industry || 'Cinema')}</span><span class="rating-badge">${rating === 'DEMO' ? 'SAMPLE' : '★ ' + rating}</span></div><div class="movie-meta"><h4 class="movie-title" title="${esc(movie.title)}">${esc(movie.title)}</h4><div class="movie-subtitle"><span>${esc(movie.year || (movie.release_date || '').slice(0, 4) || 'Year N/A')}</span><span>${esc((movie.genre_names || [])[0] || 'Movie')}</span></div><div class="genre-pills">${genre}</div></div></article>`;
>>>>>>> origin/main
  }
  function bindMovieCards(containerSelector) {
    $$(containerSelector + ' img').forEach((img) => {
      if (img.dataset.fallbackBound) return;
      img.dataset.fallbackBound = '1';
      img.addEventListener('error', () => {
        const title = (img.alt || 'Movie poster').replace(/ poster$/i, '');
        const panel = document.createElement('div'); panel.className = 'poster-fallback';
        const mark = document.createElement('span'); mark.className = 'fallback-mark'; mark.textContent = '▶';
        const label = document.createElement('span'); label.textContent = 'POSTER UNAVAILABLE';
        const strong = document.createElement('strong'); strong.textContent = title;
        panel.append(mark, label, strong); img.replaceWith(panel);
      }, { once: true });
    });
    $$(containerSelector + ' .movie-card').forEach((card) => {
      const open = () => openMovie(card.dataset.movieId);
      card.addEventListener('click', open);
      card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    });
  }
  function renderMovies(movies, append = false) {
    const grid = $('#movie-grid');
    $('#empty-state').classList.toggle('hidden', movies.length > 0);
    if (!append) grid.innerHTML = '';
    if (movies.length) grid.insertAdjacentHTML('beforeend', movies.map(renderCard).join(''));
    bindMovieCards('#movie-grid');
<<<<<<< HEAD
    $('#results-count').textContent = `${state.query ? 'Search results' : 'Showing'} ${state.movies.length} title${state.movies.length === 1 ? '' : 's'}${state.live ? ' · Local dataset' : ' · offline samples'}`;
=======
    $('#results-count').textContent = `${state.query ? 'Search results' : 'Showing'} ${state.movies.length} title${state.movies.length === 1 ? '' : 's'}${state.live ? ' · live metadata' : ' · offline samples'}`;
>>>>>>> origin/main
    updateStats(); populateRecommendationSelect(); renderDatasetTable();
  }
  function updateStats() {
    $('#stat-count').textContent = fmtNum(state.movies.length);
    const ratings = state.movies.map(m => Number(m.vote_average)).filter(n => Number.isFinite(n) && n > 0);
    $('#stat-rating').textContent = ratings.length ? (ratings.reduce((a,b) => a+b, 0) / ratings.length).toFixed(1) + '/10' : 'N/A';
<<<<<<< HEAD
    $('#stat-boxoffice').textContent = state.live ? 'Check dataset fields' : 'Not available';
    $('#results-title').textContent = state.query ? `Search: “${state.query}”` : CATEGORIES[state.category];
    $('#section-subtitle').textContent = `${INDUSTRIES[state.industry]} · ${state.live ? 'Downloaded movie metadata' : 'Install the downloadable movie dataset to enable the full catalogue'}.`;
=======
    $('#stat-boxoffice').textContent = state.live ? 'API values' : 'Demo mode';
    $('#results-title').textContent = state.query ? `Search: “${state.query}”` : CATEGORIES[state.category];
    $('#section-subtitle').textContent = `${INDUSTRIES[state.industry]} · ${state.live ? 'Current movie metadata from TMDB' : 'Sample titles until API credentials are configured'}.`;
>>>>>>> origin/main
  }
  async function fetchMovies({ append = false, refresh = false } = {}) {
    if (state.loading) return;
    state.loading = true;
    if (!append) $('#movie-grid').innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
    $('#results-count').textContent = 'Fetching movie data…';
    try {
      const params = new URLSearchParams({ industry: state.industry, category: state.category, page: String(state.page), q: state.query });
      if (refresh) params.set('refresh', '1');
      const response = await fetch(`/api/movies?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Could not load movie records');
      const movies = payload.results || [];
      state.live = Boolean(payload.live);
      state.movies = append ? state.movies.concat(movies) : movies;
      if (!append) state.movies = movies;
<<<<<<< HEAD
      setStatus(state.live, state.live ? 'Local dataset' : 'Dataset not installed');
=======
      setStatus(state.live, state.live ? 'TMDB live data' : 'Offline sample mode');
>>>>>>> origin/main
      showNotice(payload.warning || payload.notice || '', payload.warning ? 'error' : '');
      renderMovies(movies, append);
      $('#load-more').classList.toggle('hidden', !state.live || state.page >= (payload.total_pages || 1) || movies.length === 0);
    } catch (error) {
<<<<<<< HEAD
      // If this exact filter was never cached, keep the last saved catalogue useful offline.
      const saved = state.movies.filter((movie) => {
        const industryMatch = state.industry === 'all' || String(movie.industry || '').toLowerCase() === state.industry;
        const haystack = [movie.title, ...(movie.genre_names || [])].join(' ').toLowerCase();
        return industryMatch && (!state.query || haystack.includes(state.query.toLowerCase()));
      });
      state.live = false;
      if (saved.length) {
        showNotice('Showing previously saved catalogue results. New searches need an internet connection.', '');
        setStatus(false, 'Saved offline catalogue');
        renderMovies(saved);
        $('#results-count').textContent = `${saved.length} saved title${saved.length === 1 ? '' : 's'} · offline cache`;
      } else {
        showNotice(`Unable to fetch movies: ${error.message}`, 'error');
        $('#movie-grid').innerHTML = '';
        $('#empty-state').classList.remove('hidden');
        $('#results-count').textContent = 'No saved results for this selection';
      }
=======
      showNotice(`Unable to fetch movies: ${error.message}`, 'error');
      $('#movie-grid').innerHTML = '';
      $('#empty-state').classList.remove('hidden');
      $('#results-count').textContent = 'Could not load records';
>>>>>>> origin/main
    } finally { state.loading = false; }
  }
  async function fetchStatus() {
    try {
      const response = await fetch('/api/status'); const data = await response.json();
<<<<<<< HEAD
      setStatus(data.live, data.live ? 'Local dataset' : 'Dataset not installed');
      if (!data.live) showNotice('You are viewing the offline sample. To enable live movie search, metadata and dataset ratings, run py scripts/download_dataset.py to install the large local movie catalogue. No movie API key is required.');
=======
      setStatus(data.live, data.live ? 'TMDB live data' : 'Offline sample mode');
      if (!data.live) showNotice('You are viewing the offline sample. To enable current TMDB posters, ratings, search and available financial details, add your TMDB API Read Access Token to the .env file. This demo does not fabricate box-office values.');
>>>>>>> origin/main
    } catch (_) { setStatus(false, 'Local website'); }
  }
  function activateView(view) {
    state.activeView = view;
    $$('.nav-link').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
    ['discover','boxoffice','recommendations','dataset'].forEach(name => $(`#${name}-view`).classList.toggle('hidden', name !== view));
    $('#hero').classList.toggle('hidden', view !== 'discover');
    $('.toolbar').classList.toggle('hidden', view !== 'discover');
    showNotice('');
    if (view === 'boxoffice') loadBoxOffice();
    if (view === 'dataset') renderDatasetTable();
    if (view === 'recommendations') populateRecommendationSelect();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  async function loadBoxOffice(refresh = false) {
    $('#boxoffice-note').textContent = 'Loading available financial information…';
    $('#box-chart').innerHTML = '<div class="skeleton-card" style="min-height:140px"></div>';
    try {
      const params = new URLSearchParams({ industry: state.industry }); if (refresh) params.set('refresh', '1');
      const response = await fetch(`/api/box-office?${params.toString()}`); const payload = await response.json();
      state.boxOffice = payload.results || [];
      $('#boxoffice-note').textContent = payload.notice || payload.warning || 'Financial data loaded.';
      $('#boxoffice-note').classList.toggle('demo-warning', Boolean(payload.illustrative_demo));
      const complete = state.boxOffice.filter(m => Number(m.budget) > 0 && Number(m.revenue) > 0);
      $('#box-count').textContent = fmtNum(complete.length);
      const totalRevenue = complete.reduce((sum,m) => sum + Number(m.revenue), 0);
      $('#box-revenue').textContent = totalRevenue ? fmtMoney(totalRevenue) : 'Not available';
      const top = complete.slice().sort((a,b) => Number(b.revenue) - Number(a.revenue))[0];
      $('#box-top').textContent = top ? fmtMoney(top.revenue) : '—';
      $('#box-top-title').textContent = top ? top.title : 'No reported revenue found';
      const rois = complete.map(m => Number(m.roi)).filter(Number.isFinite);
      $('#box-roi').textContent = rois.length ? (rois.reduce((a,b) => a+b, 0) / rois.length).toFixed(1) + '%' : '—';
      renderBoxChart(complete); renderBoxTable(state.boxOffice);
    } catch (error) { $('#boxoffice-note').textContent = `Unable to load data: ${error.message}`; $('#box-chart').innerHTML = '<div class="box-empty">Could not load box-office data.</div>'; }
  }
  function renderBoxChart(movies) {
    const chart = $('#box-chart');
    if (!movies.length) { chart.innerHTML = '<div class="box-empty">No budget and revenue pairs are available for this selection.</div>'; return; }
    const max = Math.max(...movies.map(m => Number(m.revenue) || 0), 1);
    chart.innerHTML = movies.slice(0, 12).map(m => `<div class="chart-row"><span class="chart-label" title="${esc(m.title)}">${esc(m.title)}</span><div class="chart-track"><div class="chart-fill" style="width:${Math.max(1,(Number(m.revenue)||0)/max*100)}%"></div></div><span class="chart-number">${fmtMoney(m.revenue)}</span></div>`).join('');
  }
  function renderBoxTable(movies) {
    const body = $('#box-table-body');
    if (!movies.length) { body.innerHTML = '<tr><td colspan="6">No financial records are available for this selection.</td></tr>'; return; }
    body.innerHTML = movies.map(m => `<tr><td>${esc(m.title)}</td><td>${esc(m.industry || 'International')}</td><td>${fmtMoney(m.budget)}</td><td>${fmtMoney(m.revenue)}</td><td>${m.profit != null ? fmtMoney(m.profit) : '—'}</td><td>${m.roi != null && Number.isFinite(Number(m.roi)) ? Number(m.roi).toFixed(1)+'%' : '—'}</td></tr>`).join('');
  }
<<<<<<< HEAD
  function populateRecommendationSelect(extraMovie = null) {
    const select = $('#recommend-source'); const selected = select.value;
    const uniq = new Map(); [...state.movies, ...state.boxOffice, ...(extraMovie ? [extraMovie] : [])].forEach(m => { if (m.id != null) uniq.set(String(m.id), m); });
    const items = [...uniq.values()];
    if (!items.length) { select.innerHTML = '<option value="">No movies loaded</option>'; return; }
    select.innerHTML = items.map(m => `<option value="${esc(m.id)}">${esc(m.title)} · ${esc(m.industry || 'Cinema')}</option>`).join('');
    const preferred = extraMovie ? String(extraMovie.id) : selected;
    if ([...select.options].some(o => o.value === preferred)) select.value = preferred;
=======
  function populateRecommendationSelect() {
    const select = $('#recommend-source'); const selected = select.value;
    const uniq = new Map(); [...state.movies, ...state.boxOffice].forEach(m => { if (m.id != null) uniq.set(String(m.id), m); });
    const items = [...uniq.values()];
    if (!items.length) { select.innerHTML = '<option value="">No movies loaded</option>'; return; }
    select.innerHTML = items.map(m => `<option value="${esc(m.id)}">${esc(m.title)} · ${esc(m.industry || 'Cinema')}</option>`).join('');
    if ([...select.options].some(o => o.value === selected)) select.value = selected;
>>>>>>> origin/main
  }
  async function runRecommendations() {
    const id = $('#recommend-source').value;
    if (!id) { toast('Load or choose a movie first.'); return; }
    $('#recommend-count').textContent = 'Finding related titles…'; $('#recommend-grid').innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
    try {
      const response = await fetch(`/api/movie/${encodeURIComponent(id)}/recommendations`); const payload = await response.json();
<<<<<<< HEAD
      if (!response.ok) throw new Error(payload.error || 'Could not load recommendations');
      const movies = payload.results || [];
      $('#recommend-count').textContent = `${movies.length} recommendation${movies.length === 1 ? '' : 's'}${payload.live ? ' from local dataset' : ' in sample data'}`;
      $('#recommend-grid').innerHTML = movies.length ? movies.map(renderCard).join('') : `<div class="box-empty">${esc(payload.message || 'No suitable matches were found. Try another movie.')}</div>`;
      bindMovieCards('#recommend-grid');
    } catch (error) {
      const source = getMovie(id);
      const sourceGenres = new Set(source?.genre_names || []);
      const local = source ? state.movies.filter((movie) => String(movie.id) !== String(id)).map((movie) => {
        const overlap = (movie.genre_names || []).filter((genre) => sourceGenres.has(genre)).length;
        const sameIndustry = movie.industry === source.industry ? 1 : 0;
        return { movie, score: overlap * 3 + sameIndustry };
      }).filter((item) => item.score > 0).sort((a, b) => b.score - a.score).slice(0, 6).map((item) => item.movie) : [];
      $('#recommend-count').textContent = `${local.length} saved-catalogue recommendation${local.length === 1 ? '' : 's'} · offline`;
      $('#recommend-grid').innerHTML = local.length ? local.map(renderCard).join('') : `<div class="box-empty">No suitable saved recommendations are available. (${esc(error.message)})</div>`;
      bindMovieCards('#recommend-grid');
    }
=======
      const movies = payload.results || [];
      $('#recommend-count').textContent = `${movies.length} recommendation${movies.length === 1 ? '' : 's'}${payload.live ? ' from TMDB' : ' in sample data'}`;
      $('#recommend-grid').innerHTML = movies.length ? movies.map(renderCard).join('') : '<div class="box-empty">No recommendations are available. Configure live API credentials or choose another title.</div>';
      bindMovieCards('#recommend-grid');
    } catch (error) { $('#recommend-count').textContent = 'Recommendations unavailable'; $('#recommend-grid').innerHTML = `<div class="box-empty">${esc(error.message)}</div>`; }
>>>>>>> origin/main
  }
  function renderDatasetTable() {
    const body = $('#dataset-table-body'); const filter = ($('#table-search')?.value || '').toLowerCase();
    const list = state.movies.filter(m => !filter || [m.title,m.industry,m.year,m.original_language,(m.genre_names||[]).join(' ')].join(' ').toLowerCase().includes(filter));
<<<<<<< HEAD
    if (!list.length) { body.innerHTML = '<tr><td colspan="6">No matching records.</td></tr>'; $('#dataset-caption').textContent = state.live ? 'Local downloaded movie metadata.' : 'Offline sample dataset; live ratings and financial values are not filled with fabricated values.'; return; }
    body.innerHTML = list.map(m => `<tr><td>${esc(m.title)}</td><td>${esc(m.industry || 'International')}</td><td>${esc(m.year || (m.release_date||'').slice(0,4) || '—')}</td><td>${esc(LANGUAGES[m.original_language] || m.original_language || '—')}</td><td>${esc((m.genre_names||[]).join(', ') || '—')}</td><td>${m.vote_average != null && Number(m.vote_average)>0 ? Number(m.vote_average).toFixed(1)+'/10' : '—'}</td></tr>`).join('');
    $('#dataset-caption').textContent = state.live ? `${state.movies.length} records received from local dataset. Language-based industry labels are approximate.` : `${state.movies.length} sample titles. Install the full dataset for the complete catalogue.`;
=======
    if (!list.length) { body.innerHTML = '<tr><td colspan="6">No matching records.</td></tr>'; $('#dataset-caption').textContent = state.live ? 'Live TMDB metadata.' : 'Offline sample dataset; live ratings and financial values are not filled with fabricated values.'; return; }
    body.innerHTML = list.map(m => `<tr><td>${esc(m.title)}</td><td>${esc(m.industry || 'International')}</td><td>${esc(m.year || (m.release_date||'').slice(0,4) || '—')}</td><td>${esc(LANGUAGES[m.original_language] || m.original_language || '—')}</td><td>${esc((m.genre_names||[]).join(', ') || '—')}</td><td>${m.vote_average != null && Number(m.vote_average)>0 ? Number(m.vote_average).toFixed(1)+'/10' : '—'}</td></tr>`).join('');
    $('#dataset-caption').textContent = state.live ? `${state.movies.length} records received from TMDB. Language-based industry labels are approximate.` : `${state.movies.length} curated offline sample titles. No live ratings or financial figures are claimed.`;
>>>>>>> origin/main
  }
  function exportCsv() {
    const columns = ['title','industry','release_date','original_language','genre_names','vote_average','budget','revenue','overview'];
    const lines = [columns.join(','), ...state.movies.map(m => columns.map(k => { let v = k === 'genre_names' ? (m[k]||[]).join(' | ') : (m[k] ?? ''); return `"${String(v).replace(/"/g,'""')}"`; }).join(','))];
    const blob = new Blob(['\ufeff' + lines.join('\r\n')], {type:'text/csv;charset=utf-8;'}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='cinescope_movies.csv'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); toast('CSV export downloaded.');
  }
  async function openMovie(id) {
    const modal = $('#movie-modal'); const content = $('#modal-content'); modal.classList.remove('hidden'); document.body.style.overflow = 'hidden'; content.innerHTML = '<div style="padding:32px;color:#a7b1c1">Loading movie details…</div>';
    try {
      const response = await fetch(`/api/movie/${encodeURIComponent(id)}`); const movie = await response.json();
      if (!response.ok) throw new Error(movie.error || 'Movie details unavailable');
<<<<<<< HEAD
      const poster = movie.poster_url || ('');
      const year = movie.year || (movie.release_date || '').slice(0,4) || '—';
      const rating = movie.vote_average != null && Number(movie.vote_average)>0 ? Number(movie.vote_average).toFixed(1)+'/10' : 'Not reported';
      const roi = Number(movie.budget)>0 && Number(movie.revenue)>0 ? (((Number(movie.revenue)-Number(movie.budget))/Number(movie.budget))*100).toFixed(1)+'%' : 'Not available';
      content.innerHTML = `<div class="modal-layout"><div>${poster ? `<img class="modal-poster" src="${esc(poster)}" alt="${esc(movie.title)} poster">` : `<div class="modal-poster poster-fallback">${fallbackPoster(movie)}</div>`}<p style="margin:10px 0 0"><span class="live-tag">${movie.live ? 'DATASET RECORD' : 'SAMPLE RECORD'}</span></p></div><div class="modal-main"><p class="eyebrow">${esc(movie.industry || 'CINEMA')} · ${esc(year)}</p><h2 class="modal-title" id="modal-title">${esc(movie.title)}</h2>${movie.tagline ? `<p style="color:var(--accent);font-style:italic">${esc(movie.tagline)}</p>` : ''}<p class="modal-overview">${esc(movie.overview || 'Synopsis not available.')}</p><div class="genre-pills">${(movie.genre_names||[]).map(g=>`<span class="genre-pill">${esc(g)}</span>`).join('')}</div><div class="modal-facts"><div class="modal-fact"><span>DATASET RATING</span><strong>${esc(rating)}</strong></div><div class="modal-fact"><span>RUNTIME</span><strong>${movie.runtime ? esc(movie.runtime+' min') : '—'}</strong></div><div class="modal-fact"><span>VOTES</span><strong>${movie.vote_count ? fmtNum(movie.vote_count) : '—'}</strong></div><div class="modal-fact"><span>CERTIFICATION</span><strong>${esc(movie.certification || '—')}</strong></div><div class="modal-fact"><span>BOX OFFICE</span><strong>Not supplied</strong></div></div><p class="muted small">${movie.live ? 'Live metadata and audience rating from local dataset. Financial fields are shown only when the source provides them. IMDb IDs link to IMDb when available.' : 'Offline sample record. No financial figures or ratings have been fabricated.'}</p>${movie.directors?.length ? `<p class="muted small"><b>Director:</b> ${esc(movie.directors.join(', '))}</p>` : ''}${movie.writers?.length ? `<p class="muted small"><b>Writers:</b> ${esc(movie.writers.join(', '))}</p>` : ''}${movie.cast?.length ? `<p class="muted small"><b>Cast:</b> ${esc(movie.cast.map(x=>x.name).filter(Boolean).join(', '))}</p>` : ''}${movie.imdb_url ? `<p><a class="button button-secondary" href="${esc(movie.imdb_url)}" target="_blank" rel="noopener">Open IMDb page ↗</a></p>` : ''}<button class="button button-primary" id="modal-recommend">Find similar movies ↗</button></div></div>`;
      $('#modal-recommend').addEventListener('click', () => { $('#movie-modal').classList.add('hidden'); document.body.style.overflow=''; activateView('recommendations'); populateRecommendationSelect(movie); runRecommendations(); });
    } catch (error) {
      const movie = getMovie(id);
      if (!movie) { content.innerHTML = `<div style="padding:30px"><h3>Could not load details</h3><p class="muted">${esc(error.message)}</p></div>`; return; }
      content.innerHTML = `<div class="modal-layout"><div>${movie.poster_url ? `<img class="modal-poster" src="${esc(movie.poster_url)}" alt="${esc(movie.title)} poster">` : `<div class="modal-poster poster-fallback">${fallbackPoster(movie)}</div>`}</div><div class="modal-main"><p class="eyebrow">SAVED OFFLINE RECORD</p><h2 class="modal-title" id="modal-title">${esc(movie.title)}</h2><p class="modal-overview">${esc(movie.overview || 'Synopsis not available in the saved record.')}</p><div class="genre-pills">${(movie.genre_names || []).map((genre) => `<span class="genre-pill">${esc(genre)}</span>`).join('')}</div><p class="muted small">This is a saved catalogue summary. Reconnect for full movie details and any newly available provider data.</p></div></div>`;
    }
=======
      const poster = movie.poster_url || (movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '');
      const year = movie.year || (movie.release_date || '').slice(0,4) || '—';
      const rating = movie.vote_average != null && Number(movie.vote_average)>0 ? Number(movie.vote_average).toFixed(1)+'/10' : 'Not reported';
      const roi = Number(movie.budget)>0 && Number(movie.revenue)>0 ? (((Number(movie.revenue)-Number(movie.budget))/Number(movie.budget))*100).toFixed(1)+'%' : 'Not available';
      content.innerHTML = `<div class="modal-layout"><div>${poster ? `<img class="modal-poster" src="${esc(poster)}" alt="${esc(movie.title)} poster">` : `<div class="modal-poster poster-fallback">${fallbackPoster(movie)}</div>`}<p style="margin:10px 0 0"><span class="live-tag">${movie.live ? 'LIVE TMDB' : 'SAMPLE RECORD'}</span></p></div><div class="modal-main"><p class="eyebrow">${esc(movie.industry || 'CINEMA')} · ${esc(year)}</p><h2 class="modal-title" id="modal-title">${esc(movie.title)}</h2>${movie.tagline ? `<p style="color:var(--accent);font-style:italic">${esc(movie.tagline)}</p>` : ''}<p class="modal-overview">${esc(movie.overview || 'Synopsis not available.')}</p><div class="genre-pills">${(movie.genre_names||[]).map(g=>`<span class="genre-pill">${esc(g)}</span>`).join('')}</div><div class="modal-facts"><div class="modal-fact"><span>RATING</span><strong>${esc(rating)}</strong></div><div class="modal-fact"><span>RUNTIME</span><strong>${movie.runtime ? esc(movie.runtime+' min') : '—'}</strong></div><div class="modal-fact"><span>BUDGET</span><strong>${fmtMoney(movie.budget)}</strong></div><div class="modal-fact"><span>REVENUE</span><strong>${fmtMoney(movie.revenue)}</strong></div><div class="modal-fact"><span>PROFIT (REPORTED)</span><strong>${Number(movie.budget)>0&&Number(movie.revenue)>0 ? fmtMoney(Number(movie.revenue)-Number(movie.budget)) : '—'}</strong></div><div class="modal-fact"><span>SIMPLE ROI</span><strong>${roi}</strong></div></div><p class="muted small">${movie.live ? 'Live metadata from TMDB; budget and revenue may be missing or incomplete.' : 'Offline sample record. No financial figures or ratings have been fabricated.'}</p><button class="button button-primary" id="modal-recommend">Find similar movies ↗</button></div></div>`;
      $('#modal-recommend').addEventListener('click', () => { $('#movie-modal').classList.add('hidden'); document.body.style.overflow=''; activateView('recommendations'); populateRecommendationSelect(); if ([...$('#recommend-source').options].some(o=>o.value===String(movie.id))) $('#recommend-source').value=String(movie.id); runRecommendations(); });
    } catch (error) { content.innerHTML = `<div style="padding:30px"><h3>Could not load details</h3><p class="muted">${esc(error.message)}</p></div>`; }
>>>>>>> origin/main
  }
  function closeModal() { $('#movie-modal').classList.add('hidden'); document.body.style.overflow=''; }

  $$('.nav-link').forEach(btn => btn.addEventListener('click', () => activateView(btn.dataset.view)));
  $$('.industry-chip').forEach(btn => btn.addEventListener('click', () => { $$('.industry-chip').forEach(x => x.classList.toggle('active', x === btn)); state.industry=btn.dataset.industry; state.page=1; fetchMovies(); if (state.activeView === 'boxoffice') loadBoxOffice(); }));
  $$('.category-chip[data-category]').forEach(btn => btn.addEventListener('click', () => { $$('.category-chip[data-category]').forEach(x => x.classList.toggle('active', x === btn)); state.category=btn.dataset.category; state.page=1; fetchMovies(); }));
  $('#search-form').addEventListener('submit', (e) => { e.preventDefault(); state.query=$('#search-input').value.trim(); state.page=1; fetchMovies(); });
  $('#explore-button').addEventListener('click', () => $('#movie-grid').scrollIntoView({behavior:'smooth',block:'start'}));
  $('#refresh-button').addEventListener('click', () => fetchMovies({refresh:true}));
  $('#load-more').addEventListener('click', () => { state.page++; fetchMovies({append:true}); });
  $('#box-refresh').addEventListener('click', () => loadBoxOffice(true));
  $('#recommend-button').addEventListener('click', runRecommendations);
  $('#table-search').addEventListener('input', renderDatasetTable);
  $('#export-csv').addEventListener('click', exportCsv);
  $('#modal-close').addEventListener('click', closeModal);
  $('#movie-modal').addEventListener('click', (e) => { if (e.target === $('#movie-modal')) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
  $('#current-year').textContent = new Date().getFullYear();
<<<<<<< HEAD

  // Progressive Web App: connection state, installation and safe update activation.
  let deferredInstallPrompt = null;
  let waitingWorker = null;
  function updateConnectionState() {
    const online = navigator.onLine;
    const banner = $('#connection-banner');
    if (!banner) return;
    banner.classList.toggle('is-offline', !online);
    banner.classList.toggle('is-online', online);
    $('#connection-message').textContent = online
      ? 'You are online · live movie data can refresh'
      : 'You are offline · showing saved CineScope data where available';
    if (online) setTimeout(() => banner.classList.remove('is-online'), 2600);
  }
  window.addEventListener('online', () => { updateConnectionState(); toast('Connection restored. Refreshing movie data…'); fetchMovies(); if (state.activeView === 'boxoffice') loadBoxOffice(); });
  window.addEventListener('offline', () => { updateConnectionState(); toast('Offline mode enabled. Saved data remains available.'); });
  updateConnectionState();
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault(); deferredInstallPrompt = event;
    $('#install-app')?.classList.remove('hidden');
  });
  $('#install-app')?.addEventListener('click', async () => {
    if (!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    $('#install-app').classList.add('hidden');
  });
  window.addEventListener('appinstalled', () => { $('#install-app')?.classList.add('hidden'); toast('CineScope installed successfully.'); });
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js', { scope: '/' });
        if (registration.waiting) showUpdateButton(registration.waiting);
        registration.addEventListener('updatefound', () => {
          const worker = registration.installing;
          if (!worker) return;
          worker.addEventListener('statechange', () => {
            if (worker.state === 'installed' && navigator.serviceWorker.controller) showUpdateButton(worker);
          });
        });
        navigator.serviceWorker.addEventListener('controllerchange', () => window.location.reload());
      } catch (error) { console.warn('CineScope offline support could not be enabled:', error); }
    });
  }
  function showUpdateButton(worker) {
    waitingWorker = worker;
    $('#update-app')?.classList.remove('hidden');
  }
  $('#update-app')?.addEventListener('click', () => {
    if (waitingWorker) waitingWorker.postMessage({ type: 'SKIP_WAITING' });
  });

=======
>>>>>>> origin/main
  fetchStatus(); fetchMovies();
})();
