import os

from dnslib import AAAA, NS, SOA, A

BEACON_DOMAIN = os.getenv("BEACON_DOMAIN", "metrics-7361234.ru")

STATIC_RECORDS = [
    {
        "type": "SOA",
        "question": f"www.{BEACON_DOMAIN}",
        "answer": SOA(
            f"ns.{BEACON_DOMAIN}",
            f"admin.{BEACON_DOMAIN}",
            (2019010101, 60, 60, 60, 30),
        ),
    },
    {
        "type": "NS",
        "question": f"www.{BEACON_DOMAIN}",
        "answer": NS(f"ns.{BEACON_DOMAIN}"),
    },
    {"type": "A", "question": f"ns.{BEACON_DOMAIN}", "answer": A("192.168.85.115")},
    {"type": "A", "question": f"ns1.{BEACON_DOMAIN}", "answer": A("192.168.85.115")},
    {
        "type": "AAAA",
        "question": f"www.{BEACON_DOMAIN}",
        "answer": AAAA("fe80::f64d:30ff:fec4:b429"),
    },
]
