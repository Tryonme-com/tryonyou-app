import os

class SEOEngine:
    def __init__(self):
        self.domain = "https://tryonyou.app"
        self.patent = "PCT/EP2025/067317"
        self.founder = "Rubén Espinar Rodríguez"

    def inject_seo_tags(self, filename):
        if not os.path.exists(filename): return
        tags = f"""
        <meta name="author" content="{self.founder}">
        <meta name="description" content="TryOnYou: Le miroir numérique du futur. Brevet {self.patent}.">
        """
        with open(filename, "r") as f:
            content = f.read()
        if '<meta name="author"' not in content:
            new_content = content.replace("<head>", f"<head>{tags}")
            with open(filename, "w") as f:
                f.write(new_content)
            print(f"✅ SEO inyectado en {filename}")

    def generate_sitemap(self):
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{self.domain}/index.html</loc></url>
  <url><loc>{self.domain}/success.html</loc></url>
</urlset>"""
        with open("sitemap.xml", "w") as f:
            f.write(sitemap)
        print("✅ sitemap.xml generado.")

if __name__ == "__main__":
    engine = SEOEngine()
    engine.generate_sitemap()
    engine.inject_seo_tags("index.html")
    engine.inject_seo_tags("success.html")
