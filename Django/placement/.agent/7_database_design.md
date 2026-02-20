# 7. DATABASE DESIGN

## Overview
This document outlines the database schema and design decisions for the Placement Management System. The system uses Django's ORM with a relational database backend (SQLite for development, PostgreSQL recommended for production).

## Core Models

### 1. User Management

#### User (Django's built-in)
- **Purpose**: Base authentication and user identification
- **Key Fields**:
  - `username` (CharField): Unique identifier
  - `email` (EmailField): User email
  - `password` (CharField): Hashed password
  - `first_name`, `last_name` (CharField): User name
  - `is_active`, `is_staff`, `is_superuser` (BooleanField): Permissions

#### StudentProfile
- **Purpose**: Extended profile for student users
- **Key Fields**:
  - `user` (OneToOneField → User): Link to User model
  - `roll_number` (CharField): Unique student identifier
  - `department` (CharField): Academic department
  - `batch` (IntegerField): Graduation year
  - `cgpa` (DecimalField): Academic performance
  - `phone` (CharField): Contact number
  - `resume` (FileField): Uploaded resume
  - `is_approved` (BooleanField): Admin approval status
  - `created_at`, `updated_at` (DateTimeField): Timestamps
- **Relationships**:
  - One-to-One with User
  - One-to-Many with JobApplication
  - One-to-Many with PlacementDetail

#### CompanyProfile
- **Purpose**: Extended profile for company/recruiter users
- **Key Fields**:
  - `user` (OneToOneField → User): Link to User model
  - `company_name` (CharField): Official company name
  - `industry` (CharField): Business sector
  - `website` (URLField): Company website
  - `description` (TextField): Company overview
  - `logo` (ImageField): Company logo
  - `is_approved` (BooleanField): Admin approval status
  - `created_at`, `updated_at` (DateTimeField): Timestamps
- **Relationships**:
  - One-to-One with User
  - One-to-Many with JobPosting

### 2. Job Management

#### JobPosting
- **Purpose**: Job opportunities posted by companies
- **Key Fields**:
  - `company` (ForeignKey → CompanyProfile): Posting company
  - `title` (CharField): Job title
  - `description` (TextField): Job details
  - `requirements` (TextField): Qualification requirements
  - `location` (CharField): Job location
  - `job_type` (CharField): Full-time/Internship/Contract
  - `salary_min`, `salary_max` (DecimalField): Salary range (₹)
  - `deadline` (DateField): Application deadline
  - `is_active` (BooleanField): Posting status
  - `created_at`, `updated_at` (DateTimeField): Timestamps
- **Relationships**:
  - Many-to-One with CompanyProfile
  - One-to-Many with JobApplication

#### JobApplication
- **Purpose**: Student applications to job postings
- **Key Fields**:
  - `student` (ForeignKey → StudentProfile): Applicant
  - `job` (ForeignKey → JobPosting): Target job
  - `status` (CharField): Applied/Shortlisted/Rejected/Accepted
  - `cover_letter` (TextField): Application letter
  - `applied_at` (DateTimeField): Application timestamp
  - `updated_at` (DateTimeField): Last status update
- **Relationships**:
  - Many-to-One with StudentProfile
  - Many-to-One with JobPosting
- **Constraints**:
  - Unique together: (student, job) - prevents duplicate applications

### 3. Placement Tracking

#### PlacementDetail
- **Purpose**: Track successful placements
- **Key Fields**:
  - `student` (ForeignKey → StudentProfile): Placed student
  - `company_name` (CharField): Hiring company
  - `position` (CharField): Job title
  - `package` (DecimalField): Annual salary (₹)
  - `joining_date` (DateField): Start date
  - `placement_type` (CharField): On-campus/Off-campus
  - `created_at`, `updated_at` (DateTimeField): Timestamps
- **Relationships**:
  - Many-to-One with StudentProfile

### 4. Learning & Development (Domain System)

#### Domain
- **Purpose**: Learning tracks/skill areas
- **Key Fields**:
  - `name` (CharField): Domain name
  - `description` (TextField): Domain overview
  - `icon` (CharField): Icon identifier
  - `color` (CharField): Theme color
  - `is_active` (BooleanField): Availability status
  - `created_at` (DateTimeField): Creation timestamp
- **Relationships**:
  - Many-to-Many with StudentProfile (through enrollment)
  - One-to-Many with Resource
  - One-to-Many with Assignment

#### Resource
- **Purpose**: Learning materials within domains
- **Key Fields**:
  - `domain` (ForeignKey → Domain): Parent domain
  - `title` (CharField): Resource title
  - `description` (TextField): Resource details
  - `resource_type` (CharField): Video/Article/Document
  - `url` (URLField): Resource link
  - `file` (FileField): Uploaded file
  - `order` (IntegerField): Display order
  - `created_at` (DateTimeField): Creation timestamp
- **Relationships**:
  - Many-to-One with Domain

#### Assignment
- **Purpose**: Tasks/assessments within domains
- **Key Fields**:
  - `domain` (ForeignKey → Domain): Parent domain
  - `title` (CharField): Assignment title
  - `description` (TextField): Assignment details
  - `due_date` (DateField): Submission deadline
  - `total_marks` (IntegerField): Maximum score
  - `created_at` (DateTimeField): Creation timestamp
- **Relationships**:
  - Many-to-One with Domain
  - One-to-Many with Submission

#### Submission
- **Purpose**: Student assignment submissions
- **Key Fields**:
  - `assignment` (ForeignKey → Assignment): Target assignment
  - `student` (ForeignKey → StudentProfile): Submitting student
  - `file` (FileField): Submission file
  - `submitted_at` (DateTimeField): Submission timestamp
  - `marks` (IntegerField): Awarded score
  - `feedback` (TextField): Instructor comments
- **Relationships**:
  - Many-to-One with Assignment
  - Many-to-One with StudentProfile

## Database Relationships Diagram

```
User (1) ←→ (1) StudentProfile
                    ↓ (1)
                    ↓
                    ↓ (Many)
              JobApplication
                    ↑ (Many)
                    ↑
                    ↑ (1)
User (1) ←→ (1) CompanyProfile
                    ↓ (1)
                    ↓
                    ↓ (Many)
                JobPosting

StudentProfile (1) → (Many) PlacementDetail
StudentProfile (Many) ←→ (Many) Domain
Domain (1) → (Many) Resource
Domain (1) → (Many) Assignment
Assignment (1) → (Many) Submission (Many) ← (1) StudentProfile
```

## Indexing Strategy

### Primary Indexes (Auto-created by Django)
- All primary keys (`id` fields)
- All foreign keys
- Unique fields (`username`, `email`, `roll_number`)

### Recommended Additional Indexes
```python
# StudentProfile
indexes = [
    models.Index(fields=['batch', 'department']),
    models.Index(fields=['is_approved']),
]

# JobPosting
indexes = [
    models.Index(fields=['is_active', 'deadline']),
    models.Index(fields=['company', 'created_at']),
]

# JobApplication
indexes = [
    models.Index(fields=['student', 'status']),
    models.Index(fields=['job', 'applied_at']),
]

# PlacementDetail
indexes = [
    models.Index(fields=['student', 'joining_date']),
]
```

## Data Integrity Constraints

### Model-Level Constraints
1. **Unique Constraints**:
   - `User.username`, `User.email`
   - `StudentProfile.roll_number`
   - `(JobApplication.student, JobApplication.job)` - Composite unique

2. **Foreign Key Constraints**:
   - `ON DELETE CASCADE`: User deletion cascades to profiles
   - `ON DELETE PROTECT`: Prevent deletion of referenced companies/students
   - `ON DELETE SET_NULL`: Optional relationships (e.g., deleted resources)

3. **Check Constraints**:
   - `cgpa` between 0.0 and 10.0
   - `salary_min` ≤ `salary_max`
   - `marks` ≤ `total_marks`
   - `deadline` > current date (for active jobs)

### Application-Level Validation
- Email format validation
- Phone number format validation
- File type restrictions (resume: PDF, images: JPG/PNG)
- File size limits (resumes: 5MB, images: 2MB)

## Migration Strategy

### Initial Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding New Fields
1. Add field with `null=True` or `default` value
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Populate data if needed
5. Remove `null=True` if required (create new migration)

### Data Migrations
```python
# Example: Populate default domains
from django.db import migrations

def create_default_domains(apps, schema_editor):
    Domain = apps.get_model('app_name', 'Domain')
    domains = [
        {'name': 'Web Development', 'icon': 'code', 'color': '#3B82F6'},
        {'name': 'Data Science', 'icon': 'chart', 'color': '#10B981'},
        # ... more domains
    ]
    for domain_data in domains:
        Domain.objects.create(**domain_data)

class Migration(migrations.Migration):
    dependencies = [
        ('app_name', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_domains),
    ]
```

## Performance Considerations

### Query Optimization
1. **Select Related**: Use for one-to-one and foreign key relationships
   ```python
   StudentProfile.objects.select_related('user')
   JobApplication.objects.select_related('student', 'job')
   ```

2. **Prefetch Related**: Use for many-to-many and reverse foreign keys
   ```python
   Domain.objects.prefetch_related('resource_set', 'assignment_set')
   ```

3. **Only/Defer**: Limit fields retrieved
   ```python
   StudentProfile.objects.only('user__username', 'roll_number', 'cgpa')
   ```

### Caching Strategy
- Cache frequently accessed, rarely changed data:
  - Domain list
  - Active job postings count
  - Placement statistics
- Use Django's cache framework with Redis/Memcached

### Database Connection Pooling
- Use `CONN_MAX_AGE` in production
- Configure connection pool size based on concurrent users

## Backup and Recovery

### Backup Strategy
1. **Daily automated backups**:
   ```bash
   python manage.py dumpdata > backup_$(date +%Y%m%d).json
   ```

2. **Database-level backups** (PostgreSQL):
   ```bash
   pg_dump dbname > backup_$(date +%Y%m%d).sql
   ```

3. **File storage backups**: Media files (resumes, logos, submissions)

### Recovery Procedure
```bash
# From JSON dump
python manage.py loaddata backup_20260206.json

# From SQL dump (PostgreSQL)
psql dbname < backup_20260206.sql
```

## Security Considerations

1. **Sensitive Data**:
   - Passwords: Hashed using Django's PBKDF2 algorithm
   - Personal information: Encrypted at rest (production)
   - File uploads: Validated and scanned

2. **Access Control**:
   - Row-level permissions via Django's auth system
   - Students can only view their own applications
   - Companies can only view applications to their jobs
   - Admins have full access

3. **SQL Injection Prevention**:
   - Use Django ORM (parameterized queries)
   - Avoid raw SQL where possible
   - Sanitize inputs in raw queries

## Scalability Considerations

### Horizontal Scaling
- Database replication (read replicas)
- Sharding strategy for large datasets
- Separate databases for analytics

### Vertical Scaling
- Increase database server resources
- Optimize queries and indexes
- Implement database partitioning

### Archive Strategy
- Move old job postings to archive table
- Compress old submissions
- Retain placement data indefinitely for alumni tracking

## Future Enhancements

1. **Analytics Tables**:
   - Materialized views for placement statistics
   - Aggregated data for reporting dashboards

2. **Audit Logging**:
   - Track all data modifications
   - Store user actions for compliance

3. **Full-Text Search**:
   - PostgreSQL full-text search for job descriptions
   - Elasticsearch integration for advanced search

4. **Time-Series Data**:
   - Application trends over time
   - Placement statistics by year/department

---

**Last Updated**: 2026-02-06  
**Version**: 1.0  
**Maintained By**: Development Team
