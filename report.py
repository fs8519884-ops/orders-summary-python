from datetime import datetime

def get_orders_summary(data, from_, to, group_by, min_amount=None):
    """
    Generates a summary of orders grouped by either 'day' or 'customer'.
    
    :param data: list of order dictionaries
    :param from_: start date string (YYYY-MM-DD, inclusive)
    :param to: end date string (YYYY-MM-DD, inclusive)
    :param group_by: "day" or "customer"
    :param min_amount: minimum computed order amount (optional)
    """
    # Parse boundary dates for robust comparison
    start_date = datetime.strptime(from_, "%Y-%m-%d").date()
    end_date = datetime.strptime(to, "%Y-%m-%d").date()
    
    # Dictionary to hold our grouped aggregations
    # Structure: { group_key: [order_amounts, ...] }
    groups = {}
    
    for order in data:
        # 1. Parse and filter by date
        order_date_str = order.get("orderDate", "").split("T")[0] # Handles full ISO timestamps safely
        try:
            order_date = datetime.strptime(order_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue # Skip order if date format is invalid
            
        if not (start_date <= order_date <= end_date):
            continue
            
        # 2. Calculate the total order amount from line items
        # Formula: sum(quantity * unitPrice)
        line_items = order.get("lineItems", [])
        order_amount = sum(
            item.get("quantity", 0) * item.get("unitPrice", 0.0) 
            for item in line_items
        )
        
        # 3. Filter by min_amount if provided
        if min_amount is not None and order_amount < min_amount:
            continue
            
        # 4. Determine the grouping key
        if group_by == "day":
            group_key = order_date_str
        elif group_by == "customer":
            group_key = order.get("customerId")
        else:
            continue # Skip if group_by configuration is unknown
            
        if group_key is None:
            continue
            
        # 5. Collect order amount into the respective group
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(order_amount)
        
    # 6. Build and aggregate the final summary list
    summary = []
    for key, amounts in groups.items():
        total_amount = sum(amounts)
        count = len(amounts)
        avg_amount = total_amount / count if count > 0 else 0.0
        
        summary.append({
            "key": key,
            "count": count,
            "totalAmount": round(total_amount, 2),  # Rounded to 2 decimal places for currency safety
            "avgAmount": round(avg_amount, 2)
        })
        
    # 7. Return results sorted by key ascending
    return sorted(summary, key=lambda x: x["key"])
