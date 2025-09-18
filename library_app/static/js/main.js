/*  library_app/static/js/main.js
    Enthält den client-seitigen JavaScript-Code für interaktive Funktionen der Anwendung,
    wie die Autovervollständigung für Autoren und die dynamische Höhenanpassung der Tabellen.
*/

// Dynamische Anpassung der Tabellengröße
function adjustTableHeight() {
    const tableContainer = document.querySelector('.table-container');

    if (!tableContainer) {
        return;
    }

    const topOffset = tableContainer.getBoundingClientRect().top;
    const bottomMargin = 20; 
    const availableHeight = window.innerHeight - topOffset - bottomMargin;

    tableContainer.style.maxHeight = Math.max(200, availableHeight) + 'px';
}

// Diese Funktion initialisiert die Autocomplete-Funktionalität für Autorennamen
function initializeAuthorAutocomplete() {
    const input = document.getElementById("author_name_input");

    if (!input) { return; }

    const suggestionsContainer = document.getElementById("author_suggestions");
    input.addEventListener("input", function(e) {
        const query = this.value;
        closeAllLists();
        if (!query || query.length < 1) { return false; }
        fetch(`/api/search_authors?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsContainer.innerHTML = '';
                data.forEach(authorName => {
                    const suggestionDiv = document.createElement("DIV");
                    suggestionDiv.innerHTML = "<strong>" + authorName.substr(0, query.length) + "</strong>";
                    suggestionDiv.innerHTML += authorName.substr(query.length);
                    suggestionDiv.addEventListener("click", function(e) {
                        input.value = authorName;
                        closeAllLists();
                    });
                    suggestionsContainer.appendChild(suggestionDiv);
                });
            });
    });

    function closeAllLists(elmnt) {
        suggestionsContainer.innerHTML = '';
    }

    document.addEventListener("click", function (e) {
        if (e.target != input) {
            closeAllLists();
        }
    });
}

// Führt Funktionen nach dem Laden der Seite aus
document.addEventListener('DOMContentLoaded', () => {
    adjustTableHeight();
    initializeAuthorAutocomplete();
});

// Führt die Höhenanpassung aus, wenn das Fenster in der Größe geändert wird
window.addEventListener('resize', adjustTableHeight);