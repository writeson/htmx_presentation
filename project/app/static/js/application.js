document.addEventListener('DOMContentLoaded', () => {
    // Mock data
    let tracks = Array.from({length: 50}, (_, i) => ({
        id: i + 1,
        name: `Track ${i + 1}`,
        artist: `Artist ${Math.floor(i / 3) + 1}`,
        album: `Album ${Math.floor(i / 5) + 1}`,
        duration: `${Math.floor(Math.random() * 5) + 2}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
        price: '$0.99',
        genre: ['Rock', 'Pop', 'Jazz', 'Classical'][Math.floor(Math.random() * 4)],
        releaseDate: `202${Math.floor(Math.random() * 4)}`
    }));

// State management
    let state = {
        currentPage: 1,
        itemsPerPage: 10,
        sortField: null,
        sortDirection: 'asc',
        filterText: '',
        filterField: 'all'
    };

// Sorting function
    function sortData(data, field, direction) {
        return [...data].sort((a, b) => {
            let comparison = a[field] > b[field] ? 1 : -1;
            return direction === 'asc' ? comparison : -comparison;
        });
    }

// Filtering function
    function filterData(data) {
        if (!state.filterText) return data;

        return data.filter(item => {
            if (state.filterField === 'all') {
                return Object.values(item).some(val =>
                    String(val).toLowerCase().includes(state.filterText.toLowerCase())
                );
            }
            return String(item[state.filterField])
                .toLowerCase()
                .includes(state.filterText.toLowerCase());
        });
    }

    // Update table function
    function updateTable() {
        const filteredData = filterData(tracks);
        const sortedData = state.sortField
            ? sortData(filteredData, state.sortField, state.sortDirection)
            : filteredData;

        const start = (state.currentPage - 1) * state.itemsPerPage;
        const paginatedData = sortedData.slice(start, start + state.itemsPerPage);

        const tbody = document.getElementById('tracks-body');
        tbody.innerHTML = '';

        paginatedData.forEach(track => {
            const row = document.createElement('tr');
            row.innerHTML = `
        <td>${track.album}</td>
        <td>${track.artist}</td>
        <td>${track.duration}</td>
        <td>${track.price}</td>
        <td>
          <button class="button is-small is-info view-details" data-id="${track.id}">
            <span class="icon is-small">
              <i class="fas fa-info-circle"></i>
            </span>
          </button>
        </td>
      `;
            tbody.appendChild(row);
        });

        updatePagination(filteredData.length);
        document.getElementById('totalItems').textContent = filteredData.length;
    }

    // Update pagination controls
    function updatePagination(totalItems) {
        const totalPages = Math.ceil(totalItems / state.itemsPerPage);
        const paginationList = document.querySelector('.pagination-list');
        paginationList.innerHTML = '';

        // Previous button
        document.querySelector('.pagination-previous').disabled = state.currentPage === 1;
        document.querySelector('.pagination-next').disabled = state.currentPage === totalPages;

        // Generate page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || Math.abs(i - state.currentPage) <= 1) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.className = `pagination-link ${i === state.currentPage ? 'is-current' : ''}`;
                a.setAttribute('aria-label', `Go to page ${i}`);
                a.textContent = i;
                a.onclick = () => {
                    state.currentPage = i;
                    updateTable();
                };
                li.appendChild(a);
                paginationList.appendChild(li);
            } else if (i === 2 || i === totalPages - 1) {
                const li = document.createElement('li');
                const span = document.createElement('span');
                span.className = 'pagination-ellipsis';
                span.innerHTML = '&hellip;';
                li.appendChild(span);
                paginationList.appendChild(li);
            }
        }
    }

    // Event Listeners
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.addEventListener('click', () => {
            const field = icon.dataset.sort;
            if (state.sortField === field) {
                state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                state.sortField = field;
                state.sortDirection = 'asc';
            }

            // Update sort icons
            document.querySelectorAll('.sort-icon').forEach(i => {
                i.querySelector('i').className = 'fas fa-sort';
                i.classList.remove('active');
            });

            icon.classList.add('active');
            icon.querySelector('i').className = `fas fa-sort-${state.sortDirection === 'asc' ? 'up' : 'down'}`;

            state.currentPage = 1;
            updateTable();
        });
    });

    document.getElementById('searchInput').addEventListener('input', (e) => {
        state.filterText = e.target.value;
        state.currentPage = 1;
        updateTable();
    });

    document.getElementById('filterField').addEventListener('change', (e) => {
        state.filterField = e.target.value;
        state.currentPage = 1;
        updateTable();
    });

    document.getElementById('itemsPerPage').addEventListener('change', (e) => {
        state.itemsPerPage = parseInt(e.target.value);
        state.currentPage = 1;
        updateTable();
    });

    document.querySelector('.pagination-previous').addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            updateTable();
        }
    });

    document.querySelector('.pagination-next').addEventListener('click', () => {
        const totalPages = Math.ceil(filterData(tracks).length / state.itemsPerPage);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            updateTable();
        }
    });

    // Modal functionality
    document.addEventListener('click', (e) => {
        if (e.target.closest('.view-details')) {
            const trackId = e.target.closest('.view-details').dataset.id;
            const track = tracks.find(t => t.id === parseInt(trackId));

            const modal = document.getElementById('trackModal');
            modal.querySelector('.modal-card-body').innerHTML = `
        <div class="content">
          <h3>${track.name}</h3>
          <p><strong>Artist:</strong> ${track.artist}</p>
          <p><strong>Album:</strong> ${track.album}</p>
          <p><strong>Duration:</strong> ${track.duration}</p>
          <p><strong>Price:</strong> ${track.price}</p>
          <p><strong>Genre:</strong> ${track.genre}</p>
          <p><strong>Release Date:</strong> ${track.releaseDate}</p>
        </div>
      `;
            modal.classList.add('is-active');
        }
    });

    // Close modal
    document.querySelectorAll('.modal .delete, .modal .button').forEach(button => {
        button.addEventListener('click', () => {
            document.getElementById('trackModal').classList.remove('is-active');
        });
    });

    // Initial load
    updateTable();
});
