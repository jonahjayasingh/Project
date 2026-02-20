from .models import Website_Course,Website_Gallery,website_Placement, website_services,company_career,website_project_domain,website_project,company_contacts,company_applicant
from django.shortcuts import redirect
from django.contrib import messages
def website_course_create(request):
    id = request.POST.get("id")
    cname = request.POST.get("course_name")
    cdescription = request.POST.get("course_description")
    cduration = request.POST.get("course_duration")
    image = request.FILES.get("course_thumbnail")
    cdifficulty = request.POST.get("course_difficulty")
    cprice = request.POST.get("course_price")
    if id:
        course = Website_Course.objects.get(id=id)
        course.course_name = cname
        course.course_description = cdescription
        course.course_duration = cduration
        course.course_difficulty = cdifficulty
        course.course_price = cprice
        if image:
            course.course_thumbnail.delete()
            course.course_thumbnail = image
        course.save()
        messages.success(request,"Course updated successfully")
        return redirect("app:website_details")
    else:
        Website_Course.objects.create(
            user=request.user,
            course_name=cname,
            course_description=cdescription,
            course_duration=cduration,
            course_thumbnail=image,
            course_difficulty=cdifficulty,
            course_price=cprice
        )
        messages.success(request,"Course created successfully")
        return redirect("app:website_details")
    
def website_course_delete(request):
    print(request.POST)
    course_id = request.POST.get("id")
    print(course_id)
    if course_id != None:
        print(Website_Course.objects.filter(id=3))
        course = Website_Course.objects.get(id=course_id)
        course.delete()
        messages.success(request,"Course deleted successfully")
        print("hello")
        return redirect("app:website_details")
    else:
        messages.error(request,"Course not found")
        return redirect("app:website_details")
        
def website_gallery_create(request):
    id = request.POST.get("id")
    image = request.FILES.get("gallery_image")
    if id:
        gallery = Website_Gallery.objects.get(id=id)
        if image:
            gallery.gallery_image.delete()
            gallery.gallery_image = image
        gallery.gallery_title = request.POST.get("gallery_title")
        gallery.save()
        messages.success(request,"Gallery image updated successfully")
        return redirect("app:website_details")
    else:
        if image:
            Website_Gallery.objects.create(
                user=request.user,
                gallery_title=request.POST.get("gallery_title"),
                gallery_image=image
            )
            messages.success(request,"Gallery image created successfully")
            return redirect("app:website_details")
        else:
            messages.error(request,"Gallery image not found")
            return redirect("app:website_details")

def website_gallery_delete(request):
    id = request.POST.get("id")
    if id:
        gallery = Website_Gallery.objects.get(id=id)
        gallery.delete()
        messages.success(request,"Gallery image deleted successfully")
        return redirect("app:website_details")
    else:
        messages.error(request,"Gallery image not found")
        return redirect("app:website_details")

def website_placement_create(request):
    id = request.POST.get("id")
    op = request.POST.get("op")
    pname = request.POST.get("name")
    pdescription = request.POST.get("description")
    pjob_title = request.POST.get("job_title")
    pjob_company = request.POST.get("job_company")
    pimage = request.FILES.get("image")

    if id:
        placement = website_Placement.objects.get(id=id)
        placement.name = pname
        placement.description = pdescription
        placement.job_title = pjob_title
        placement.job_company = pjob_company
        if pimage:
            placement.image.delete()
            placement.image = pimage
        placement.save()
        messages.success(request,"Placement updated successfully")
        return redirect("app:website_details")
    else:
        website_Placement.objects.create(
            user=request.user,
            name=pname,
            description=pdescription,
            job_title=pjob_title,
            job_company=pjob_company,
            image=pimage
        )
        messages.success(request,"Placement created successfully")
        return redirect("app:website_details")

def website_placement_delete(request):
    id = request.POST.get("id")
    if id:
        placement = website_Placement.objects.get(id=id)
        placement.delete()
        messages.success(request,"Placement deleted successfully")
        return redirect("app:website_details")
    else:
        messages.error(request,"Placement not found")
        return redirect("app:website_details")

def website_service_create(request):
    id = request.POST.get("id")
    sname = request.POST.get("name")
    sdescription = request.POST.get("description")
    simage = request.FILES.get("image")
    skey_points = request.POST.get("key_points")
    if id:
        service = website_services.objects.get(id=id)
        service.name = sname
        service.description = sdescription
        service.key_points = [item.strip() for item in skey_points.split('.') if item.strip()]
        if simage:
            service.image.delete()
            service.image = simage
        service.save()
        messages.success(request,"Service updated successfully")
        return redirect("app:website_details")
    else:
        website_services.objects.create(
            user=request.user,
            name=sname,
            description=sdescription,
            image=simage,
            key_points= [item.strip() for item in skey_points.split('.') if item.strip()]
        )
        messages.success(request,"Service created successfully")
        return redirect("app:website_details")
    
def website_service_delete(request):
    id = request.POST.get("id")
    if id:
        service = website_services.objects.get(id = id)
        service.delete()
        messages.success(request,"Service deleted successfully")
        return redirect('app:website_details')
    else:
        messages.error(request,'Service not found')
        return redirect('app:website_details')

def website_domain_create(request):
    id = request.POST.get('id')
    name = request.POST.get('domain_name')
    description = request.POST.get('domain_description')
    image = request.FILES.get('domain_image')
    if id:
        domain = website_project_domain.objects.get(id = id)
        domain.name = name
        domain.description = description
        if image:
            domain.image.delete()
            domain.image = image
        domain.save()
        messages.success(request,"Project Domain is updated successfully")
        return redirect("app:website_details")
    else:
        website_project_domain.objects.create(
            user= request.user,
            name = name,
            description= description,
            image= image
        )
        messages.success(request,"Project domain add successfully")
        return redirect("app:website_details")
     
        
def website_domain_delete(request):
    id = request.POST.get("id")
    if id:
        domain = website_project_domain.objects.get(id = id)
        domain.delete()
        messages.success(request,"Project domain deleted successfully")
        return redirect('app:website_details')
    else:
        messages.error(request,'Project domain not found')
        return redirect('app:website_details')

def website_project_create(request):
    id = request.POST.get('id')
    pname = request.POST.get('name')
    pdescription = request.POST.get('description')
    domain = request.POST.get('domain')
    print(request.POST)
    if id:
        project = website_project.objects.get(id = id)
        project.name = pname
        project.description = pdescription  
        project.domain = website_project_domain.objects.get(id= domain)
        project.save()
        messages.success(request,"Project is updated successfully")
        return redirect("app:website_details")
    else:
        website_project.objects.create(
            name = pname,
            description= pdescription,
            domain = website_project_domain.objects.get(id= domain)
        )
        messages.success(request,"Project add successfully")
        return redirect("app:website_details")

def website_project_delete(request):
    id = request.POST.get("id")
    if id:
        project = website_project.objects.get(id = id)
        project.delete()
        messages.success(request,"Project deleted successfully")
        return redirect('app:website_details')
    else:
        messages.error(request,'Project not found')
        return redirect('app:website_details')


def website_contact_create(request):
    print(request.POST)
    id = request.POST.get('id')
    phone1 = request.POST.get('phone1')
    phone2 = request.POST.get('phone2')
    email = request.POST.get('email')
    address = request.POST.get('address')
    linkedin = request.POST.get('linkedin_url')
    twitter = request.POST.get('twitter_url')
    facebook = request.POST.get('facebook_url')
    instagram = request.POST.get('instagram_url')
    youtube = request.POST.get('youtube_url')
    map_emp = request.POST.get("map_url")
    if id:
        contact = company_contacts.objects.get(id = id)
        contact.phone1 = phone1
        contact.phone2 = phone2
        contact.email = email
        contact.address = address
        contact.linkedin = linkedin
        contact.twitter = twitter
        contact.facebook = facebook
        contact.instagram = instagram
        contact.youtube = youtube
        contact.map_embed_url = map_emp
        contact.save()
        messages.success(request,"Contact is updated successfully")
        return redirect("app:website_details")
    else:
        company_contacts.objects.create(
            user= request.user,
            phone1 = phone1,
            phone2 = phone2,
            email = email,
            whatsapp = phone1,
            address = address,
            linkedin = linkedin,
            twitter = twitter,
            facebook = facebook,
            instagram = instagram,
            youtube = youtube,
            map_embed_url=map_emp
        )
        messages.success(request,"Contact add successfully")
        return redirect("app:website_details")



def website_career_create(request):
    id = request.POST.get('id')
    title = request.POST.get('title')
    description = request.POST.get('description')
    key_responsibilities = request.POST.get('key_responsibilities').split('.')
    location = request.POST.get('location')
    job_type = request.POST.get('job_type')
    experience = request.POST.get('experience')
    application_Deadline = request.POST.get('application_Deadline')
    if id:
        career = company_career.objects.get(id = id)    
        career.title = title
        career.description = description
        career.location = location
        career.job_type = job_type
        career.experience = experience
        career.key_responsibilities = key_responsibilities
        career.application_Deadline = application_Deadline
        career.save()
        messages.success(request,"Career is updated successfully")
        return redirect("app:website_details")
    else:
        company_career.objects.create(
            user= request.user,
            title = title,
            description = description,
            location = location,
            job_type = job_type,
            experience = experience,
            application_Deadline = application_Deadline,

            key_responsibilities = key_responsibilities
        )
        messages.success(request,"Career add successfully")
        return redirect("app:website_details")
    
def website_career_delete(request):
    id = request.POST.get("id")
    if id:
        project = company_career.objects.get(id = id)
        applicants  = company_applicant.objects.filter(career=id)
        print(applicants)
        applicants.delete()
        # project.delete()
        messages.success(request,"Career deleted successfully")
        return redirect('app:website_details')
    else:
        messages.error(request,'Career not found')
        return redirect('app:website_details')
