


function confirmDelete(event, itemName) {
    if (!confirm(`Вы уверены, что хотите удалить ${itemName}?`)) {
        event.preventDefault();
    }
}


function setupTableSearch(inputId, tableId, columnIndex = 0) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchText = this.value.toLowerCase().trim();
        const rows = document.querySelectorAll(`#${tableId} tbody tr`);
        
        rows.forEach(row => {
            const cell = row.cells[columnIndex];
            if (cell) {
                const text = cell.textContent.toLowerCase();
                if (searchText === '' || text.includes(searchText)) {
                    row.style.display = '';
                    if (searchText !== '' && text.includes(searchText)) {
                        row.classList.add('highlight');
                    } else {
                        row.classList.remove('highlight');
                    }
                } else {
                    row.style.display = 'none';
                }
            }
        });
    });
}


function recalcRow(row) {
    const select = row.querySelector('.product-select');
    const priceSpan = row.querySelector('.price');
    const stockSpan = row.querySelector('.stock');
    const qtyInput = row.querySelector('.qty');
    const lineTotalSpan = row.querySelector('.line-total');

    if (!select || !qtyInput) return;

    const option = select.options[select.selectedIndex];
    const price = parseFloat(option?.dataset?.price || 0);
    const stock = parseFloat(option?.dataset?.stock || 0);
    const qty = parseFloat(qtyInput.value || 0);

    if (priceSpan) priceSpan.textContent = price.toFixed(2);
    if (stockSpan) stockSpan.textContent = stock.toFixed(2);

    const lineTotal = price * qty;
    if (lineTotalSpan) lineTotalSpan.textContent = lineTotal.toFixed(2);

    
    if (stockSpan) {
        stockSpan.classList.remove('stock-ok', 'stock-bad');
        if (qty <= stock && qty > 0) {
            stockSpan.classList.add('stock-ok');
        } else if (qty > stock) {
            stockSpan.classList.add('stock-bad');
            
            const beep = document.getElementById('beep');
            if (beep) beep.play().catch(e => console.log('Audio play failed:', e));
        }
    }

    recalcOrderTotal();
}


function recalcOrderTotal() {
    let total = 0;
    document.querySelectorAll('#order-items tbody tr').forEach(row => {
        const lineTotal = parseFloat(row.querySelector('.line-total')?.textContent || 0);
        total += lineTotal;
    });
    
    const orderTotal = document.getElementById('order-total');
    if (orderTotal) {
        orderTotal.textContent = total.toFixed(2);
    }
    
    
    checkCreditWarning(total);
}


function checkCreditWarning(orderTotal) {
    const paymentType = document.querySelector('input[name="payment_type"]:checked')?.value;
    if (paymentType !== 'credit') return;

    const clientSelect = document.getElementById('client-select');
    if (!clientSelect) return;

    const option = clientSelect.options[clientSelect.selectedIndex];
    const creditLimit = parseFloat(option?.dataset?.creditLimit || 0);
    const currentDebt = parseFloat(option?.dataset?.currentDebt || 0);

    if (!creditLimit) return;

    const newDebt = currentDebt + orderTotal;
    const threshold = creditLimit * 0.9;

    if (newDebt >= threshold) {
        alert('Внимание: текущий долг с учетом этого заказа превысит 90% кредитного лимита!');
    }
}


function addOrderRow() {
    const tbody = document.querySelector('#order-items tbody');
    if (!tbody) return;

    const rowCount = tbody.children.length;
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-index', rowCount);
    
    
    const productsHtml = document.getElementById('products-options')?.innerHTML || '';
    
    newRow.innerHTML = `
        <td>
            <select name="item-${rowCount}-product" class="product-select form-control">
                <option value="">-- Выберите товар --</option>
                ${productsHtml}
            </select>
        </td>
        <td><span class="price">0.00</span></td>
        <td><span class="stock">0.00</span></td>
        <td><input type="number" name="item-${rowCount}-qty" class="qty form-control" min="0" step="0.01" value="0"></td>
        <td><span class="line-total">0.00</span></td>
        <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove(); recalcOrderTotal();">✕</button></td>
    `;
    
    tbody.appendChild(newRow);
    
    
    newRow.querySelector('.product-select').addEventListener('change', () => recalcRow(newRow));
    newRow.querySelector('.qty').addEventListener('input', () => recalcRow(newRow));
}


