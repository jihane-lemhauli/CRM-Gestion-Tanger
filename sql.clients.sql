-- 1. Création de la base de données
CREATE DATABASE GestionClients_Tanger;
USE GestionClients_Tanger;

-- 2. Création de la table des clients
CREATE TABLE Clients (
    id_client INT PRIMARY KEY AUTO_INCREMENT,
    nom_client VARCHAR(100) UNIQUE,
    type_client VARCHAR(50), -- (Particulier, PME, Commune)
    telephone VARCHAR(20),
    email VARCHAR(100),
    adresse VARCHAR(255),
    ville VARCHAR(50) DEFAULT 'Tanger'
);

-- 3. Création de la table des factures (projets)
CREATE TABLE Factures (
    id_facture INT PRIMARY KEY AUTO_INCREMENT,
    nom_client_ref VARCHAR(100),
    projet VARCHAR(100),
    montant DECIMAL(10,2),
    statut VARCHAR(20), -- (Payée / En attente)
    
    -- Clé étrangère liée à la table Clients
    FOREIGN KEY (nom_client_ref) REFERENCES Clients(nom_client)
);
INSERT INTO Clients (nom_client, type_client, telephone, email, adresse) VALUES
('Sani Tanger Sarl', 'PME', '0539301020', 'contact@sanitanger.ma', 'Zone Franche Gzenaya'),
('Ahmed El Amrani', 'Particulier', '0661223344', 'ahmed.amrani@email.com', 'Marshane'),
('Commune de Tanger', 'Commune', '0539940011', 'info@villedetanger.ma', 'Hôtel de Ville'),
('Hôtel Detroit', 'PME', '0539324500', 'booking@detroit-hotel.ma', 'Malabata'),
('Boulangerie Al Jila', 'PME', '0539331515', 'aljila.tng@gmail.com', 'Boulevard Pasteur'),
('Meryem Bensalah', 'Particulier', '0662556677', 'meryem.b@email.com', 'Quartier California'),
('Technopark Tangier', 'PME', '0539391200', 'contact@technopark.ma', 'Pavillon International'),
('Yassine Mansouri', 'Particulier', '0670889900', 'y.mansouri@email.com', 'Castilla'),
('Garage Atlas', 'PME', '0539351040', 'atlas.garage@email.com', 'Route de Tétouan'),
('Café Panorama', 'PME', '0539371818', 'panorama.tng@email.com', 'Corniche');

INSERT INTO Factures (nom_client_ref, projet, montant, statut) VALUES
('Sani Tanger Sarl', 'Maintenance', 15000, 'Payée'),
('Ahmed El Amrani', 'Réparation', 2500, 'En attente'),
('Commune de Tanger', 'Audit', 85000, 'En attente'),
('Hôtel Detroit', 'Rénovation', 45000, 'Payée'),
('Boulangerie Al Jila', 'Matériel', 12000, 'Payée'),
('Sani Tanger Sarl', 'Réseau', 22000, 'En attente');
-- Remplacer NULL par 0 and all
SELECT 
    c.nom_client, 
    c.type_client, 
    c.telephone, 
    COALESCE(SUM(f.montant), 0) AS Chiffre_Affaires_Total,
    COALESCE(SUM(CASE WHEN f.statut = 'En attente' THEN f.montant ELSE 0 END), 0) AS Total_En_Attente
FROM Clients c
LEFT JOIN Factures f ON c.nom_client = f.nom_client_ref
GROUP BY c.nom_client, c.type_client, c.telephone;

SELECT 
    c.nom_client, 
    c.telephone, 
    c.email,
    SUM(f.montant) AS Chiffre_Affaires_Total,
    SUM(CASE WHEN f.statut = 'En attente' THEN f.montant ELSE 0 END) AS Total_En_Attente
FROM Clients c
LEFT JOIN Factures f ON c.nom_client = f.nom_client_ref
WHERE c.nom_client = 'Sani Tanger Sarl'
GROUP BY c.nom_client;
