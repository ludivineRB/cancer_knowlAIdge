from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import re
from urllib.parse import urljoin



class CancerInfoScraper:
    def __init__(self, headless=True, output_dir="cancer_data"):
        """Initialise le scraper avec les options Chrome"""
        self.driver = None
        self.base_url = "https://www.cancer.org"
        self.visited_urls = set()
        self.scraped_data = []
        self.retry_count = 3
        self.output_dir = output_dir
        self.progress_file = os.path.join(output_dir, "progress.log")
        self.setup_driver(headless)
        self.setup_output_directory()

    def setup_output_directory(self):
        """Crée le répertoire de sortie et initialise le fichier de progression"""
        os.makedirs(self.output_dir, exist_ok=True)

        # Créer/initialiser le fichier de progression
        if not os.path.exists(self.progress_file):
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                f.write("=== PROGRESSION DU SCRAPING ===\n")
                f.write(f"Démarrage: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Status: EN COURS\n\n")

    def log_progress(self, message):
        """Ajoute une ligne au fichier de progression"""
        try:
            with open(self.progress_file, 'a', encoding='utf-8') as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] {message}\n")
        except Exception as e:
            print(f"Erreur lors de l'écriture du log: {e}")

    def save_single_file(self, cancer_type, url, content):
        """Sauvegarde immédiatement un fichier"""
        try:
            # Nettoyer le nom du fichier
            filename = re.sub(r'[<>:"/\\|?*]', '_', cancer_type)
            filename = f"{filename}.txt"
            filepath = os.path.join(self.output_dir, filename)

            # Vérifier si le fichier existe déjà
            if os.path.exists(filepath):
                # Ajouter un numéro pour éviter les doublons
                base_name = filename.replace('.txt', '')
                counter = 1
                while os.path.exists(os.path.join(self.output_dir, f"{base_name}_{counter}.txt")):
                    counter += 1
                filename = f"{base_name}_{counter}.txt"
                filepath = os.path.join(self.output_dir, filename)

            # Sauvegarder le fichier
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Sauvegardé: {filename}")
            self.log_progress(f"Fichier sauvegardé: {filename}")
            return True

        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {cancer_type}: {e}")
            self.log_progress(f"ERREUR sauvegarde: {cancer_type} - {e}")
            return False
    def setup_driver(self, headless):
        """Configure le driver Chrome avec les options appropriées"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Chrome/91.0.4472.124 Safari/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def safe_get(self, url):
        """Navigue vers une URL de manière sécurisée avec retry"""
        for attempt in range(self.retry_count):
            try:
                if url in self.visited_urls:
                    return False
                self.visited_urls.add(url)
                self.driver.get(url)
                time.sleep(3)  # Attendre le chargement
                return True
            except Exception as e:
                print(
                    f"Erreur lors du chargement de {url}"
                    f"(tentative {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt < self.retry_count - 1:
                    time.sleep(2)  # Attendre avant retry
                else:
                    return False

    def clean_text(self, text):
        """Nettoie le texte extrait"""
        if not text:
            return ""
        # Supprimer les espaces multiples et les sauts de ligne
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_paragraphs(self, url, cancer_type):
        """Extrait tous les paragraphes d'une page finale"""
        if not self.safe_get(url):
            return

        try:
            # Attendre que la page se charge complètement
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Attendre un peu plus pour s'assurer que tout est chargé
            time.sleep(2)

            # Extraire tous les paragraphes
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")

            if paragraphs:
                content = []
                content.append(f"=== {cancer_type} ===")
                content.append(f"URL: {url}")
                content.append(f"Date de récupération: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                content.append("")

                valid_paragraphs = 0
                for i, p in enumerate(paragraphs, 1):
                    try:
                        text = self.clean_text(p.text)
                        if text and len(text) > 20:  # Ignorer les paragraphes très courts
                            content.append(f"Paragraphe {valid_paragraphs + 1}: {text}")
                            content.append("")
                            valid_paragraphs += 1
                    except Exception as e:
                        print(f"Erreur lors de l'extraction du paragraphe {i}: {e}")
                        continue

                if valid_paragraphs > 0:
                    content_str = '\n'.join(content)

                    # Sauvegarder immédiatement
                    if self.save_single_file(cancer_type, url, content_str):
                        # Ajouter aussi à la liste pour le résumé final
                        self.scraped_data.append({
                            'cancer_type': cancer_type,
                            'url': url,
                            'content': content_str
                        })
                        print(
                            f"✓ Données extraites pour {cancer_type} "
                            f"({valid_paragraphs} paragraphes valides)"
                        )
                    else:
                        print(f"✗ Échec de la sauvegarde pour {cancer_type}")
                else:
                    print(f"⚠ Aucun paragraphe valide trouvé pour {cancer_type}")
                    self.log_progress(f"Aucun paragraphe valide: {cancer_type}")
            else:
                print(f"⚠ Aucun paragraphe trouvé pour {cancer_type}")
                self.log_progress(f"Aucun paragraphe trouvé: {cancer_type}")

        except TimeoutException:
            print(f"Timeout lors de l'extraction des paragraphes pour {cancer_type}")
            self.log_progress(f"TIMEOUT: {cancer_type}")
        except Exception as e:
            print(f"Erreur lors de l'extraction des paragraphes pour {cancer_type}: {e}")
            self.log_progress(f"ERREUR extraction: {cancer_type} - {e}")

    def process_cmp_list_items(self, url, cancer_type):
        """Traite les éléments cmp-list__item-title"""
        if not self.safe_get(url):
            return

        try:
            # Chercher les liens avec la classe cmp-list__item-title
            title_links = self.driver.find_elements(By.CSS_SELECTOR, "a.cmp-list__item-title")

            if title_links:
                print(f"Trouvé {len(title_links)} liens cmp-list__item-title pour {cancer_type}")
                for link in title_links:
                    try:
                        href = link.get_attribute("href")
                        title = self.clean_text(link.text)
                        if href and title:
                            full_url = urljoin(self.base_url, href)
                            print(f"  → Extraction des données pour: {title}")
                            self.extract_paragraphs(full_url, f"{cancer_type} - {title}")
                    except Exception as e:
                        print(f"Erreur lors du traitement du lien title: {e}")
            else:
                # Si pas de cmp-list__item-title, extraire directement les paragraphes
                print(f"Pas de cmp-list__item-title trouvé, extraction directe pour {cancer_type}")
                self.extract_paragraphs(url, cancer_type)

        except Exception as e:
            print(f"Erreur lors du traitement des cmp-list items: {e}")

    def process_card_containers(self, url, cancer_type):
        """Traite les card containers récursivement"""
        if not self.safe_get(url):
            return

        try:
            # Chercher les card containers
            card_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.card__container.clickable-card")

            if card_containers:
                print(f"Trouvé {len(card_containers)} card containers pour {cancer_type}")
                for card in card_containers:
                    try:
                        # Chercher le lien dans le card
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute("href")
                        title = self.clean_text(link.text)

                        if href and title:
                            full_url = urljoin(self.base_url, href)
                            print(f"  → Traitement du card: {title}")
                            # Traiter récursivement (peut contenir d'autres cards ou des cmp-list items)
                            self.process_card_containers(full_url, f"{cancer_type} - {title}")
                    except NoSuchElementException:
                        continue
                    except Exception as e:
                        print(f"Erreur lors du traitement du card: {e}")
            else:
                # Si pas de card containers, chercher les cmp-list items
                print(f"Pas de card containers, recherche des cmp-list items pour {cancer_type}")
                self.process_cmp_list_items(url, cancer_type)

        except Exception as e:
            print(f"Erreur lors du traitement des card containers: {e}")

    def scrape_cancer_types(self):
        """Fonction principale pour scraper tous les types de cancer"""
        start_url = "https://www.cancer.org/cancer/types.html"

        print("Début du scraping des types de cancer...")

        if not self.safe_get(start_url):
            print("Impossible de charger la page principale")
            return

        try:
            # Attendre que la page se charge
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.cmp-list__item"))
            )

            # Extraire d'abord tous les liens avant de les traiter
            cancer_links = []
            cancer_items = self.driver.find_elements(By.CSS_SELECTOR, "li.cmp-list__item")
            print(f"Trouvé {len(cancer_items)} types de cancer")

            for i, item in enumerate(cancer_items, 1):
                try:
                    # Chercher le lien dans l'item
                    link = item.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute("href")
                    cancer_name = self.clean_text(link.text)

                    if href and cancer_name:
                        full_url = urljoin(self.base_url, href)
                        cancer_links.append({
                            'name': cancer_name,
                            'url': full_url,
                            'index': i
                        })

                except NoSuchElementException:
                    print(f"Pas de lien trouvé dans l'item {i}")
                    continue
                except Exception as e:
                    print(f"Erreur lors de l'extraction du lien {i}: {e}")
                    continue

            print(f"Extraction terminée: {len(cancer_links)} liens valides trouvés")

            # Maintenant traiter chaque lien
            for link_data in cancer_links:
                try:
                    print(f"\n[{link_data['index']}/{len(cancer_items)}] Traitement de: {link_data['name']}")
                    print(f"URL: {link_data['url']}")
                    self.log_progress(f"Début traitement: {link_data['name']}")

                    # Traiter ce type de cancer
                    self.process_card_containers(link_data['url'], link_data['name'])

                    self.log_progress(f"Fin traitement: {link_data['name']}")

                    # Petite pause entre chaque traitement
                    time.sleep(1)

                except Exception as e:
                    print(f"Erreur lors du traitement de {link_data['name']}: {e}")
                    self.log_progress(f"ERREUR: {link_data['name']} - {e}")
                    continue

        except TimeoutException:
            print("Timeout lors du chargement de la page principale")
        except Exception as e:
            print(f"Erreur générale: {e}")

    def save_to_files(self, output_dir=None):
        """Sauvegarde le résumé final (les fichiers individuels sont déjà sauvegardés)"""
        if output_dir is None:
            output_dir = self.output_dir

        if not self.scraped_data:
            print("Aucune donnée à résumer (fichiers individuels déjà sauvegardés)")
            return

        # Créer un fichier de résumé
        summary_path = os.path.join(output_dir, "RESUME_FINAL.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== RÉSUMÉ FINAL DU SCRAPING ===\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Nombre total de pages scrapées: {len(self.scraped_data)}\n")
            f.write(f"Nombre total d'URLs visitées: {len(self.visited_urls)}\n")
            f.write("\nListe des types de cancer traités:\n")
            for i, data in enumerate(self.scraped_data, 1):
                f.write(f"{i}. {data['cancer_type']}\n")
                f.write(f"   URL: {data['url']}\n")

        # Finaliser le fichier de progression
        self.log_progress("=== SCRAPING TERMINÉ ===")
        self.log_progress(f"Total: {len(self.scraped_data)} pages sauvegardées")

        print(f"✓ Résumé final sauvegardé: {summary_path}")
        print(f"✓ Progression complète: {self.progress_file}")

    def close(self):
        """Ferme le driver"""
        if self.driver:
            self.driver.quit()

# Fonction principale
def main():
    scraper = CancerInfoScraper(headless=False, output_dir="cancer_data")  # Changez à True pour mode silencieux

    try:
        print("=== SCRAPER D'INFORMATIONS SUR LE CANCER ===")
        print("Démarrage du processus de scraping...")
        print(f"Dossier de sortie: {scraper.output_dir}")
        print(f"Fichier de progression: {scraper.progress_file}")
        print("Les fichiers seront sauvegardés au fur et à mesure.\n")

        # Lancer le scraping
        scraper.scrape_cancer_types()

        # Sauvegarder le résumé final
        print(f"\nCréation du résumé final ({len(scraper.scraped_data)} pages collectées)...")
        scraper.save_to_files()

        print("\n=== SCRAPING TERMINÉ ===")
        print(f"Fichiers individuels sauvegardés dans: {scraper.output_dir}")
        print("Consultez le fichier progress.log pour voir la progression complète")

    except KeyboardInterrupt:
        print("\nArrêt du scraping demandé par l'utilisateur")
        print(f"Fichiers déjà sauvegardés disponibles dans: {scraper.output_dir}")
    except Exception as e:
        print(f"Erreur critique: {e}")
        print(f"Fichiers déjà sauvegardés disponibles dans: {scraper.output_dir}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
    def setup_driver(self, headless):
        """Configure le driver Chrome avec les options appropriées"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
            ' Chrome/91.0.4472.124 Safari/537.36'
            )

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def safe_get(self, url):
        """Navigue vers une URL de manière sécurisée avec retry"""
        for attempt in range(self.retry_count):
            try:
                if url in self.visited_urls:
                    return False
                self.visited_urls.add(url)
                self.driver.get(url)
                time.sleep(3)  # Attendre le chargement
                return True
            except Exception as e:
                print(f"Erreur lors du chargement de {url} (tentative {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(2)  # Attendre avant retry
                else:
                    return False

    def clean_text(self, text):
        """Nettoie le texte extrait"""
        if not text:
            return ""
        # Supprimer les espaces multiples et les sauts de ligne
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_paragraphs(self, url, cancer_type):
        """Extrait tous les paragraphes d'une page finale"""
        if not self.safe_get(url):
            return

        try:
            # Attendre que la page se charge complètement
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Attendre un peu plus pour s'assurer que tout est chargé
            time.sleep(2)

            # Extraire tous les paragraphes
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")

            if paragraphs:
                content = []
                content.append(f"=== {cancer_type} ===")
                content.append(f"URL: {url}")
                content.append(f"Date de récupération: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                content.append("")

                valid_paragraphs = 0
                for i, p in enumerate(paragraphs, 1):
                    try:
                        text = self.clean_text(p.text)
                        if text and len(text) > 20:  # Ignorer les paragraphes très courts
                            content.append(f"Paragraphe {valid_paragraphs + 1}: {text}")
                            content.append("")
                            valid_paragraphs += 1
                    except Exception as e:
                        print(f"Erreur lors de l'extraction du paragraphe {i}: {e}")
                        continue

                if valid_paragraphs > 0:
                    self.scraped_data.append({
                        'cancer_type': cancer_type,
                        'url': url,
                        'content': '\n'.join(content)
                    })

                    print(f"✓ Données extraites pour {cancer_type} ({valid_paragraphs} paragraphes valides)")
                else:
                    print(f"⚠ Aucun paragraphe valide trouvé pour {cancer_type}")
            else:
                print(f"⚠ Aucun paragraphe trouvé pour {cancer_type}")

        except TimeoutException:
            print(f"Timeout lors de l'extraction des paragraphes pour {cancer_type}")
        except Exception as e:
            print(f"Erreur lors de l'extraction des paragraphes pour {cancer_type}: {e}")

    def process_cmp_list_items(self, url, cancer_type):
        """Traite les éléments cmp-list__item-title"""
        if not self.safe_get(url):
            return

        try:
            # Chercher les liens avec la classe cmp-list__item-title
            title_links = self.driver.find_elements(By.CSS_SELECTOR, "a.cmp-list__item-title")

            if title_links:
                print(f"Trouvé {len(title_links)} liens cmp-list__item-title pour {cancer_type}")
                for link in title_links:
                    try:
                        href = link.get_attribute("href")
                        title = self.clean_text(link.text)
                        if href and title:
                            full_url = urljoin(self.base_url, href)
                            print(f"  → Extraction des données pour: {title}")
                            self.extract_paragraphs(full_url, f"{cancer_type} - {title}")
                    except Exception as e:
                        print(f"Erreur lors du traitement du lien title: {e}")
            else:
                # Si pas de cmp-list__item-title, extraire directement les paragraphes
                print(f"Pas de cmp-list__item-title trouvé, extraction directe pour {cancer_type}")
                self.extract_paragraphs(url, cancer_type)

        except Exception as e:
            print(f"Erreur lors du traitement des cmp-list items: {e}")

    def process_card_containers(self, url, cancer_type):
        """Traite les card containers récursivement"""
        if not self.safe_get(url):
            return

        try:
            # Chercher les card containers
            card_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.card__container.clickable-card")

            if card_containers:
                print(f"Trouvé {len(card_containers)} card containers pour {cancer_type}")
                for card in card_containers:
                    try:
                        # Chercher le lien dans le card
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute("href")
                        title = self.clean_text(link.text)

                        if href and title:
                            full_url = urljoin(self.base_url, href)
                            print(f"  → Traitement du card: {title}")
                            # Traiter récursivement (peut contenir d'autres cards ou des cmp-list items)
                            self.process_card_containers(full_url, f"{cancer_type} - {title}")
                    except NoSuchElementException:
                        continue
                    except Exception as e:
                        print(f"Erreur lors du traitement du card: {e}")
            else:
                # Si pas de card containers, chercher les cmp-list items
                print(f"Pas de card containers, recherche des cmp-list items pour {cancer_type}")
                self.process_cmp_list_items(url, cancer_type)

        except Exception as e:
            print(f"Erreur lors du traitement des card containers: {e}")

    def scrape_cancer_types(self):
        """Fonction principale pour scraper tous les types de cancer"""
        start_url = "https://www.cancer.org/cancer/types.html"

        print("Début du scraping des types de cancer...")

        if not self.safe_get(start_url):
            print("Impossible de charger la page principale")
            return

        try:
            # Attendre que la page se charge
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.cmp-list__item"))
            )

            # Extraire d'abord tous les liens avant de les traiter
            cancer_links = []
            cancer_items = self.driver.find_elements(By.CSS_SELECTOR, "li.cmp-list__item")
            print(f"Trouvé {len(cancer_items)} types de cancer")

            for i, item in enumerate(cancer_items, 1):
                try:
                    # Chercher le lien dans l'item
                    link = item.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute("href")
                    cancer_name = self.clean_text(link.text)

                    if href and cancer_name:
                        full_url = urljoin(self.base_url, href)
                        cancer_links.append({
                            'name': cancer_name,
                            'url': full_url,
                            'index': i
                        })

                except NoSuchElementException:
                    print(f"Pas de lien trouvé dans l'item {i}")
                    continue
                except Exception as e:
                    print(f"Erreur lors de l'extraction du lien {i}: {e}")
                    continue

            print(f"Extraction terminée: {len(cancer_links)} liens valides trouvés")

            # Maintenant traiter chaque lien
            for link_data in cancer_links:
                try:
                    print(f"\n[{link_data['index']}/{len(cancer_items)}] Traitement de: {link_data['name']}")
                    print(f"URL: {link_data['url']}")

                    # Traiter ce type de cancer
                    self.process_card_containers(link_data['url'], link_data['name'])

                    # Petite pause entre chaque traitement
                    time.sleep(1)

                except Exception as e:
                    print(f"Erreur lors du traitement de {link_data['name']}: {e}")
                    continue

        except TimeoutException:
            print("Timeout lors du chargement de la page principale")
        except Exception as e:
            print(f"Erreur générale: {e}")

    def save_to_files(self, output_dir="cancer_data"):
        """Sauvegarde toutes les données dans des fichiers texte"""
        if not self.scraped_data:
            print("Aucune donnée à sauvegarder")
            return

        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)

        # Sauvegarder chaque type de cancer dans un fichier séparé
        for data in self.scraped_data:
            # Nettoyer le nom du fichier
            filename = re.sub(r'[<>:"/\\|?*]', '_', data['cancer_type'])
            filename = f"{filename}.txt"
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(data['content'])
                print(f"✓ Sauvegardé: {filepath}")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde de {filename}: {e}")

        # Créer un fichier de résumé
        summary_path = os.path.join(output_dir, "RESUME.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== RÉSUMÉ DU SCRAPING ===\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Nombre total de pages scrapées: {len(self.scraped_data)}\n")
            f.write(f"Nombre total d'URLs visitées: {len(self.visited_urls)}\n")
            f.write("\nListe des types de cancer traités:\n")
            for i, data in enumerate(self.scraped_data, 1):
                f.write(f"{i}. {data['cancer_type']}\n")

        print(f"✓ Résumé sauvegardé: {summary_path}")

    def close(self):
        """Ferme le driver"""
        if self.driver:
            self.driver.quit()

# Fonction principale
def main():
    scraper = CancerInfoScraper(headless=False)  # Changez à True pour mode silencieux

    try:
        print("=== SCRAPER D'INFORMATIONS SUR LE CANCER ===")
        print("Démarrage du processus de scraping...")

        # Lancer le scraping
        scraper.scrape_cancer_types()

        # Sauvegarder les données
        print(f"\nSauvegarde des données ({len(scraper.scraped_data)} pages collectées)...")
        scraper.save_to_files()

        print("\n=== SCRAPING TERMINÉ ===")
        print("Données sauvegardées dans le dossier 'cancer_data'")

    except KeyboardInterrupt:
        print("\nArrêt du scraping demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur critique: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
