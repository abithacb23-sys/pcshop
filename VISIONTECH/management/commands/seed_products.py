from django.core.management.base import BaseCommand
from VISIONTECH.models import Category, Product, Brand

class Command(BaseCommand):
    help = "Seeds database with futuristic gaming hardware and PC parts"

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing data...")
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        self.stdout.write("Creating categories...")
        categories_data = [
            {"name": "CPUs", "icon": "bi-cpu", "description": "High performance processors for ultimate framerates and workflows."},
            {"name": "GPUs", "icon": "bi-gpu-card", "description": "Cutting-edge graphics cards for extreme raytracing and AI rendering."},
            {"name": "Motherboards", "icon": "bi-motherboard", "description": "Premium mainboards with solid power phases and PCIe Gen 5 support."},
            {"name": "RAM", "icon": "bi-memory", "description": "High-speed overclocked memory modules with customizable RGB styling."},
            {"name": "Storage", "icon": "bi-device-ssd", "description": "Ultra fast NVMe M.2 Solid State Drives with extreme read/write speeds."},
            {"name": "PSUs", "icon": "bi-lightning-charge", "description": "Solid, efficient power supply units with neat modular cabling."},
            {"name": "Cases", "icon": "bi-box", "description": "Futuristic, premium cabinets with dual tempered glass panels and customizable fans."},
            {"name": "Cooling", "icon": "bi-snow", "description": "AIO Liquid coolers and high-performance fans to keep thermals under check."}
        ]

        cats = {}
        for cdata in categories_data:
            cat = Category.objects.create(**cdata)
            cats[cat.slug] = cat

        self.stdout.write("Creating brands...")
        brands_data = [
            {"name": "AMD", "website": "https://www.amd.com", "logo_url": "https://example.com/amd-logo.png"},
            {"name": "Intel", "website": "https://www.intel.com", "logo_url": "https://example.com/intel-logo.png"},
            {"name": "NVIDIA", "website": "https://www.nvidia.com", "logo_url": "https://example.com/nvidia-logo.png"},
            {"name": "ASUS", "website": "https://www.asus.com", "logo_url": "https://example.com/asus-logo.png"},
            {"name": "MSI", "website": "https://www.msi.com", "logo_url": "https://example.com/msi-logo.png"},
            {"name": "G.Skill", "website": "https://www.gskill.com", "logo_url": "https://example.com/gskill-logo.png"},
            {"name": "Corsair", "website": "https://www.corsair.com", "logo_url": "https://example.com/corsair-logo.png"},
            {"name": "Samsung", "website": "https://www.samsung.com", "logo_url": "https://example.com/samsung-logo.png"},
            {"name": "Crucial", "website": "https://www.crucial.com", "logo_url": "https://example.com/crucial-logo.png"},
            {"name": "Lian Li", "website": "https://www.lian-li.com", "logo_url": "https://example.com/lianli-logo.png"},
            {"name": "NZXT", "website": "https://www.nzxt.com", "logo_url": "https://example.com/nzxt-logo.png"},
            {"name": "Fractal Design", "website": "https://www.fractal-design.com", "logo_url": "https://example.com/fractal-logo.png"},
            {"name": "Noctua", "website": "https://www.noctua.at", "logo_url": "https://example.com/noctua-logo.png"}
        ]

        brands = {}
        for bdata in brands_data:
            brand = Brand.objects.create(**bdata)
            brands[brand.name] = brand

        self.stdout.write("Creating products...")
        
        products_data = [
            # CPUs
            {
                "name": "AMD Ryzen 9 9950X",
                "category": cats["cpus"],
                "description": "The flagship 16-core gaming and rendering processor based on AMD's latest Zen 5 architecture. Boost clocks up to 5.7 GHz with high efficiency.",
                "price": 74999.00,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?q=80&w=1974&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 170,
                "socket": "AM5",
                "ram_type": "DDR5",
                "weight": 0.15,
                "specs": {
                    "Cores/Threads": "16 Cores / 32 Threads",
                    "Base / Boost Clock": "4.3 GHz / 5.7 GHz",
                    "L3 Cache": "64MB",
                    "PCIe Lanes": "Gen 5",
                    "Architecture": "Zen 5"
                }
            },
            {
                "name": "Intel Core i9-14900K",
                "category": cats["cpus"],
                "description": "Intel's extreme performance processor with hybrid architecture. Features 8 performance cores and 16 efficient cores to destroy productivity and gaming workloads.",
                "price": 62499.00,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1970&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 253,
                "socket": "LGA1700",
                "ram_type": "DDR5",
                "weight": 0.15,
                "specs": {
                    "Cores/Threads": "24 Cores (8P + 16E) / 32 Threads",
                    "Max Turbo Frequency": "6.0 GHz",
                    "Smart Cache": "36MB",
                    "PCIe Support": "Gen 5 & Gen 4",
                    "Integrated Graphics": "Intel UHD Graphics 770"
                }
            },
            
            # GPUs
            {
                "name": "RTX 4090 Overclock Edition 24GB",
                "category": cats["gpus"],
                "description": "The ultimate GeForce GPU. It brings an enormous leap in performance, efficiency, and AI-powered graphics. Experience ultra-high performance gaming, incredibly detailed virtual worlds with ray tracing.",
                "price": 189999.00,
                "stock": 8,
                "image_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?q=80&w=1974&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 450,
                "weight": 2.30,
                "specs": {
                    "Memory": "24GB GDDR6X",
                    "Memory Bus": "384-bit",
                    "CUDA Cores": "16384",
                    "Boost Clock": "2625 MHz",
                    "Display Connectors": "3x DisplayPort 1.4a, 1x HDMI 2.1a"
                }
            },
            {
                "name": "ASUS TUF RX 7900 XTX 24GB",
                "category": cats["gpus"],
                "description": "Experience unprecedented performance, visuals, and efficiency at 4K and beyond with AMD Radeon RX 7900 XTX graphics cards, the world's first gaming GPUs powered by AMD RDNA 3 chiplet technology.",
                "price": 99999.00,
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?q=80&w=1974&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 355,
                "weight": 1.80,
                "specs": {
                    "Memory": "24GB GDDR6",
                    "Memory Bus": "384-bit",
                    "Stream Processors": "6144",
                    "Boost Clock": "2500 MHz",
                    "Power Connectors": "2x 8-pin"
                }
            },
            
            # Motherboards
            {
                "name": "ASUS ROG Crosshair X670E Hero",
                "category": cats["motherboards"],
                "description": "Fully armed for Zen 5 AMD Ryzen processors. Features 18+2 power stages, DDR5 support, PCIe 5.0 expansion slots, dual USB4 Type-C ports, and Wi-Fi 6E connectivity.",
                "price": 64999.00,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1563770660941-20978e870e26?q=80&w=1970&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 50,
                "socket": "AM5",
                "ram_type": "DDR5",
                "form_factor": "ATX",
                "weight": 1.40,
                "specs": {
                    "Socket": "AM5",
                    "Chipset": "AMD X670E",
                    "RAM Slots": "4x DDR5 (Up to 192GB)",
                    "Expansion Slots": "2x PCIe 5.0 x16",
                    "Storage M.2": "4x M.2 (incl. 2x PCIe 5.0)"
                }
            },
            {
                "name": "MSI MPG Z790 Carbon WiFi",
                "category": cats["motherboards"],
                "description": "Carbon black aesthetics with glowing RGB styling. Optimized for 14th Gen Intel Core processors with direct 19+1+1 phases VRM power, DDR5 memory boost, and fast 2.5G LAN + Wi-Fi 6E.",
                "price": 45499.00,
                "stock": 14,
                "image_url": "https://images.unsplash.com/photo-1555664424-778a1e5e1b48?q=80&w=2070&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 55,
                "socket": "LGA1700",
                "ram_type": "DDR5",
                "form_factor": "ATX",
                "weight": 1.20,
                "specs": {
                    "Socket": "LGA1700",
                    "Chipset": "Intel Z790",
                    "RAM Slots": "4x DDR5 (Up to 192GB)",
                    "Storage M.2": "5x M.2 Slots",
                    "Audio": "Realtek ALC4080 Codec"
                }
            },
            {
                "name": "ASUS ROG Strix B650-I Gaming WiFi",
                "category": cats["motherboards"],
                "description": "An ultra-compact Mini-ITX motherboard engineered for AM5 Ryzen processors. Ideal for small form factor (SFF) custom rigs without sacrificing performance.",
                "price": 27999.00,
                "stock": 8,
                "image_url": "https://images.unsplash.com/photo-1563770660941-20978e870e26?q=80&w=1970&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 35,
                "socket": "AM5",
                "ram_type": "DDR5",
                "form_factor": "Mini-ITX",
                "weight": 0.70,
                "specs": {
                    "Socket": "AM5",
                    "Chipset": "AMD B650",
                    "RAM Slots": "2x DDR5 (Up to 96GB)",
                    "Form Factor": "Mini-ITX",
                    "Storage M.2": "2x M.2 Slots"
                }
            },
            
            # RAM
            {
                "name": "G.Skill Trident Z5 RGB 32GB DDR5 6000MHz",
                "category": cats["ram"],
                "description": "Trident Z5 RGB series DDR5 memory is the flagship G.Skill memory designed for ultra-high overclocked performance on next-gen DDR5 platforms.",
                "price": 12499.00,
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1541029071515-84cc54f84dc5?q=80&w=2070&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 8,
                "ram_type": "DDR5",
                "weight": 0.15,
                "specs": {
                    "Capacity": "32GB (16GB x 2)",
                    "Speed": "6000 MHz",
                    "Latency": "CL30-38-38-96",
                    "Voltage": "1.35V",
                    "RGB Profile": "ASUS Aura / MSI Mystic Sync"
                }
            },
            {
                "name": "Corsair Vengeance RGB 64GB DDR5 5600MHz",
                "category": cats["ram"],
                "description": "Massive capacity meets dazzling customizable RGB. Ten zone dynamic lightbars and extreme performance tailored for Intel and AMD creator systems.",
                "price": 24999.00,
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1541029071515-84cc54f84dc5?q=80&w=2070&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 12,
                "ram_type": "DDR5",
                "weight": 0.20,
                "specs": {
                    "Capacity": "64GB (32GB x 2)",
                    "Speed": "5600 MHz",
                    "Latency": "CL40-40-40-77",
                    "Voltage": "1.25V",
                    "RGB Profile": "Corsair iCUE Integration"
                }
            },
            
            # Storage
            {
                "name": "Samsung 990 Pro 2TB PCIe Gen4 NVMe M.2",
                "category": cats["storage"],
                "description": "The champion of Gen4. Experience blisteringly fast load screens and extreme transfer rates. Reach read speeds up to 7450 MB/s and write speeds up to 6900 MB/s.",
                "price": 16999.00,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=2015&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 6,
                "weight": 0.08,
                "specs": {
                    "Interface": "PCIe Gen 4.0 x4, NVMe 2.0",
                    "Sequential Read": "Up to 7,450 MB/s",
                    "Sequential Write": "Up to 6,900 MB/s",
                    "Form Factor": "M.2 (2280)",
                    "TBW Rating": "1200 TBW"
                }
            },
            {
                "name": "Crucial T700 Gen5 2TB NVMe SSD",
                "category": cats["storage"],
                "description": "Push performance limits with PCIe 5.0 SSD storage. Experience raw speed of up to 12,400 MB/s reads and 11,800 MB/s writes. Includes premium copper heatsink.",
                "price": 28999.00,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=2015&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 11,
                "weight": 0.08,
                "specs": {
                    "Interface": "PCIe Gen 5.0 x4, NVMe 2.0",
                    "Sequential Read": "Up to 12,400 MB/s",
                    "Sequential Write": "Up to 11,800 MB/s",
                    "Form Factor": "M.2 (2280) with Heatsink",
                    "MTBF": "1.5 Million Hours"
                }
            },
            
            # Cases
            {
                "name": "Lian Li O11 Dynamic EVO RGB Black",
                "category": cats["cases"],
                "description": "The legendary dual-chamber mid-tower chassis. Features front and side tempered glass panels with wrap-around L-shaped neon RGB strips. Highly custom layout options.",
                "price": 16499.00,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1974&auto=format&fit=crop",
                "is_featured": True,
                "form_factor": "ATX, Micro-ATX, Mini-ITX",
                "weight": 12.50,
                "specs": {
                    "Type": "Mid Tower Dual Chamber",
                    "Dimensions": "478mm x 290mm x 471mm",
                    "Material": "Tempered Glass, Aluminum, Steel",
                    "Max GPU Length": "455mm",
                    "Radiator Support": "Up to 3x 360mm"
                }
            },
            {
                "name": "NZXT H9 Elite Cyber Edition",
                "category": cats["cases"],
                "description": "Showcase your internal parts with seamless glass panels. Features dynamic RGB fan hub controller, triple bottom 120mm mounts, and clean modular cable channels.",
                "price": 19999.00,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1974&auto=format&fit=crop",
                "is_featured": False,
                "form_factor": "ATX, Micro-ATX",
                "weight": 14.20,
                "specs": {
                    "Type": "Mid Tower Showcase",
                    "Glass Panels": "Front, Side, Top Tempered",
                    "Fitted Fans": "3x F120 RGB Duo, 1x F120Q",
                    "Max CPU Cooler": "165mm",
                    "Weight": "13.1 kg"
                }
            },
            {
                "name": "Fractal Design Terra Jade",
                "category": cats["cases"],
                "description": "A small-form-factor Mini-ITX cabinet designed to elevate modern gaming spaces. Combining anodized aluminum shell and FSC-certified solid walnut accents.",
                "price": 18499.00,
                "stock": 7,
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1974&auto=format&fit=crop",
                "is_featured": False,
                "form_factor": "Mini-ITX",
                "weight": 3.80,
                "specs": {
                    "Type": "Small Form Factor (SFF) ITX",
                    "Volume": "10.4 Liters",
                    "Material": "Anodized Aluminum & Solid Walnut",
                    "PCIe Riser": "Included Gen 4.0 Riser",
                    "Dimensions": "343mm x 153mm x 218mm"
                }
            },
            
            # PSUs
            {
                "name": "ASUS ROG Thor 1000W Platinum II",
                "category": cats["psus"],
                "description": "The quietest 1000W power supply. Features an OLED display panel for real-time power draw tracking, modular sleeves, aura sync RGB lighting, and premium internal cooling blocks.",
                "price": 28999.00,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1974&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 1000,
                "weight": 2.80,
                "specs": {
                    "Capacity": "1000 Watts",
                    "Efficiency": "80 PLUS Platinum",
                    "Cabling": "Fully Modular",
                    "PCIe 5.0 (12VHPWR)": "Yes (1x 600W sleeve)",
                    "OLED Display": "Yes"
                }
            },
            {
                "name": "Corsair RM850x Shift 850W Gold",
                "category": cats["psus"],
                "description": "Side-interface connectors for ultra-clean cable routing. Fully modular design with 80 Plus Gold certification, high temp Japanese caps, and zero-RPM fan tuning mode.",
                "price": 14499.00,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1974&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 850,
                "weight": 2.10,
                "specs": {
                    "Capacity": "850 Watts",
                    "Efficiency": "80 PLUS Gold",
                    "Cabling": "Side Modular Interface",
                    "Fan Type": "140mm FDB",
                    "Warranty": "10 Years"
                }
            },
            
            # Cooling
            {
                "name": "Corsair iCUE Link H150i RGB AIO",
                "category": cats["cooling"],
                "description": "Unleash liquid performance with a 360mm high-performance radiator, QX120 RGB fans, and smart single-cable linking interface. Keeps CPUs locked in freezing temperatures.",
                "price": 22999.00,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1970&auto=format&fit=crop",
                "is_featured": True,
                "wattage": 25,
                "weight": 2.10,
                "specs": {
                    "Radiator Size": "360mm",
                    "Fans": "3x QX120 RGB (Up to 2400 RPM)",
                    "Cold Plate": "Split-flow Copper",
                    "Tubing": "400mm Sleeved Rubber",
                    "Software": "iCUE Compatible"
                }
            },
            {
                "name": "Noctua NH-D15 chromax.black",
                "category": cats["cooling"],
                "description": "The award-winning air cooler master. Dual tower layout with 6 heatpipes and dual NF-A15 premium 140mm PWM silent fans. Ditch AIO liquid leaks while keeping cooling efficiency.",
                "price": 11999.00,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1970&auto=format&fit=crop",
                "is_featured": False,
                "wattage": 8,
                "weight": 1.25,
                "specs": {
                    "Cooler Type": "Dual Tower Air Cooler",
                    "Fans": "2x NF-A15 HS-PWM",
                    "Heatsink Material": "Copper Base & Aluminum Fins",
                    "Socket Support": "AM5, AM4, LGA1700, LGA1200",
                    "Acoustics": "Max 24.6 dB(A)"
                }
            }
        ]

        product_brands = {
            "AMD Ryzen 9 9950X": brands["AMD"],
            "Intel Core i9-14900K": brands["Intel"],
            "RTX 4090 Overclock Edition 24GB": brands["NVIDIA"],
            "ASUS TUF RX 7900 XTX 24GB": brands["ASUS"],
            "ASUS ROG Crosshair X670E Hero": brands["ASUS"],
            "MSI MPG Z790 Carbon WiFi": brands["MSI"],
            "ASUS ROG Strix B650-I Gaming WiFi": brands["ASUS"],
            "G.Skill Trident Z5 RGB 32GB DDR5 6000MHz": brands["G.Skill"],
            "Corsair Vengeance RGB 64GB DDR5 5600MHz": brands["Corsair"],
            "Samsung 990 Pro 2TB PCIe Gen4 NVMe M.2": brands["Samsung"],
            "Crucial T700 Gen5 2TB NVMe SSD": brands["Crucial"],
            "Lian Li O11 Dynamic EVO RGB Black": brands["Lian Li"],
            "NZXT H9 Elite Cyber Edition": brands["NZXT"],
            "Fractal Design Terra Jade": brands["Fractal Design"],
            "ASUS ROG Thor 1000W Platinum II": brands["ASUS"],
            "Corsair RM850x Shift 850W Gold": brands["Corsair"],
            "Corsair iCUE Link H150i RGB AIO": brands["Corsair"],
            "Noctua NH-D15 chromax.black": brands["Noctua"]
        }

        for pdata in products_data:
            Product.objects.create(brand=product_brands.get(pdata["name"]), **pdata)

        self.stdout.write(self.style.SUCCESS("Successfully seeded categories, brands, and products for Overclock PC Shop!"))
