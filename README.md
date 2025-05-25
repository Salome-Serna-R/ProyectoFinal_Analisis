# Numerical Solutions

**Numerical Solutions** is a web application developed to solve numerical methods interactively. It is divided into chapters based on the topics covered in the course, and features a responsive, user-friendly interface.

---

## Chapter 1: Nonlinear Equation Solvers

Implemented methods:

- Bisection Method  
- False Position Method  
- Fixed Point Method  
- Newton-Raphson Method  
- Secant Method  
- Multiple Roots Method (Version 1 and 2)

---

## Chapter 2: Linear System Solvers

Implemented methods:

- Jacobi Method  
- Gauss-Seidel Method  
- SOR Method (Successive Over-Relaxation)

---

## Chapter 3: Interpolation Methods

Implemented methods:

- Vandermonde Method  
- Newton Interpolation Method  
- Lagrange Method  
- Linear Spline  
- Cubic Spline

---

## Group Members

- Salomé Serna  
- Jhon Fredy Alzate
- Juan David Velázquez
- Esteban Salazar  

---

## Prerequisites

- Python 3.x installed  
- `pip` installed  
- Virtualenv (optional but recommended)

---

## How to Run the Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/Salome-Serna-R/ProyectoFinal_Analisis.git


2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Create environment variables**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Modify the `.env` file with the appropriate configurations as needed.

5. **Run the server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Notes
- This project does not execute migrations as it does not use a database.
- To add additional features, follow Django's structure for views, templates, and URLs.
