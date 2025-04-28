sudo mv stripe /usr/local/bin/


stripe trigger checkout.session.completed

stripe listen --forward-to localhost:8000/api/payment/webhook/
