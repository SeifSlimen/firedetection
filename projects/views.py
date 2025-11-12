from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
from .models import *
from .forms import ProjectCreationForm
from accounts.models import CustomUser
import json

@login_required
def create_project(request):
    # Vérifier que l'utilisateur est un superviseur
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST, supervisor=request.user)
        if form.is_valid():
            try:
                project = form.save()
                messages.success(request, f'Project "{project.name}" created successfully!')
                return redirect('projects:add_zone', project_id=project.id)
            except Exception as e:  
                messages.error(request, f'An error occurred while creating the project: {str(e)}')
    else:
        form = ProjectCreationForm(supervisor=request.user)
    
    return render(request, 'projects/create_project.html', {'form': form})


@login_required
def add_zone(request, project_id):
    """
    View to add a zone (polygon) to a project.
    """
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    # Filter by ID and supervisor to ensure user has access to this project
    projet_instance = get_object_or_404(Project, id=project_id, supervisor=request.user)
    zones = Zone.objects.filter(name_project=projet_instance)
    
    # Convert JSON coordinates to JSON strings for the template
    zones_data = []
    for zone in zones:
        zones_data.append({
            'zone': zone,
            'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null'
        })

    if request.method == 'POST':
        name_zone = request.POST.get('name_zone')
        description_zone = request.POST.get('description')
        multi_polygone = request.POST.get('coords_polys')
        ajoutez_un_polygone = request.POST.get('ajoutez_un_polygone')
        
        if not name_zone or not multi_polygone:
            messages.error(request, 'Please fill in all required fields.')
            zones_data = []
            for zone in zones:
                zones_data.append({
                    'zone': zone,
                    'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null'
                })
            return render(
                request,
                'projects/add_zone.html',
                {'votre_projet': projet_instance.name, 'zones': zones, 'zones_data': zones_data}
            )
        try:
            # Convert JSON text to Python dictionary
            coords_data = json.loads(multi_polygone)

            donnees_zone = Zone(
                name_zone=name_zone,
                description_zone=description_zone,
                coords_polys=coords_data,
                name_project=projet_instance
            )
            donnees_zone.save()

            zones = Zone.objects.filter(name_project=projet_instance)
            
            # Convert JSON coordinates to JSON strings for the template
            zones_data = []
            for zone in zones:
                zones_data.append({
                    'zone': zone,
                    'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null'
                })

            if ajoutez_un_polygone:
                # User wants to add another polygon
                messages.success(request, 'Zone added successfully! You can add another one.')
                return render(
                    request,
                    'projects/add_zone.html',
                    {'votre_projet': projet_instance.name, 'zones': zones, 'zones_data': zones_data}
                )
            else:
                # Move to next step (add cameras)
                messages.success(request, 'Zones added successfully!')
                return redirect('projects:add_cam', name_zone=name_zone)

        except json.JSONDecodeError:
            messages.error(request, 'Error: Invalid coordinate format.')
        except Exception as e:
            messages.error(request, f'Error occurred while creating the zone: {str(e)}')

    # Convert JSON coordinates to JSON strings for the template
    zones_data = []
    for zone in zones:
        zones_data.append({
            'zone': zone,
            'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null'
        })
    
    return render(
        request,
        'projects/add_zone.html',
        {'votre_projet': projet_instance.name, 'zones': zones, 'zones_data': zones_data}
    )

@login_required
def add_cam(request, name_zone):
    """
    View to add a camera to a project.
    """
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    zone_instance = get_object_or_404(Zone, name_zone=name_zone)
    zones = Zone.objects.filter(name_project=zone_instance.name_project)
    cams = Cam.objects.filter(name_zone=zone_instance)
    
    # Convert JSON coordinates to JSON strings for the template
    zones_data = []
    for zone in zones:
        zones_data.append({
            'zone': zone,
            'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null'
        })
    
    cams_data = []
    for cam in cams:
        cams_data.append({
            'cam': cam,
            'coords_json': json.dumps(cam.coords_cam) if cam.coords_cam else 'null'
        })

    if request.method == 'POST':
        name_cam = request.POST.get('name_cam')
        adresse_cam = request.POST.get('adresse_cam')
        num_port = request.POST.get('num_port')
        rest_de_path = request.POST.get('rest_de_path')
        custom_url = request.POST.get('custom_url')
        description_cam = request.POST.get('description_cam')
        multi_marker = request.POST.get('coords_cam')
        ajoutez_un_cam = request.POST.get('ajoutez_un_cam')

        if not name_cam or not multi_marker:
            messages.error(request, 'Please fill in all required fields.')
            return render(
                request,
                'projects/add_cam.html',
                {
                    'project_name': zone_instance.name_project.name,
                    'zone_name': zone_instance.name_zone,
                    'zones': zones,
                    'cams': cams,
                    'zones_data': zones_data,
                    'cams_data': cams_data,
                }
            )

        try:
            # Determine RTSP URL type
            is_full_rtsp_url = bool(custom_url)

            # Convert JSON sent from frontend
            coords_data = json.loads(multi_marker)
            if not isinstance(coords_data, dict):
                raise ValueError('Invalid camera coordinate format.')

            if num_port:
                try:
                    num_port = int(num_port)
                except ValueError:
                    raise ValueError('Port number must be an integer.')
            else:
                num_port = None

            donnees_cam = Cam(
                name_cam=name_cam,
                adresse_cam=adresse_cam,
                num_port=num_port,
                rest_de_path=rest_de_path,
                custom_url=custom_url,
                is_full_rtsp_url=is_full_rtsp_url,
                description_cam=description_cam,
                coords_cam=coords_data,
                name_zone=zone_instance
            )
            # Call full_clean() to execute the model's clean() method
            try:
                donnees_cam.full_clean()
            except ValidationError as e:
                # Display validation errors
                error_messages = []
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        error_messages.extend(errors)
                else:
                    error_messages.append(str(e))
                messages.error(request, 'Validation error: ' + ' '.join(error_messages))
                return render(
                    request,
                    'projects/add_cam.html',
                    {
                        'project_name': zone_instance.name_project.name,
                        'zone_name': zone_instance.name_zone,
                        'zones': zones,
                        'cams': cams,
                        'zones_data': zones_data,
                        'cams_data': cams_data,
                    }
                )
            donnees_cam.save()

            if ajoutez_un_cam:
                # User wants to add another camera
                cams = Cam.objects.filter(name_zone=zone_instance)
                # Recalculate JSON data
                cams_data = []
                for cam in cams:
                    cams_data.append({
                        'cam': cam,
                        'coords_json': json.dumps(cam.coords_cam) if cam.coords_cam else 'null'
                    })
                messages.success(request, 'Camera added successfully! You can add another one.')
                return render(
                    request,
                    'projects/add_cam.html',
                    {
                        'project_name': zone_instance.name_project.name,
                        'zone_name': zone_instance.name_zone,
                        'zones': zones,
                        'cams': cams,
                        'zones_data': zones_data,
                        'cams_data': cams_data,
                    }
                )
            else:
                # End of addition process
                messages.success(request, 'Cameras added successfully!')
                return redirect('projects:project_list')

        except json.JSONDecodeError:
            messages.error(request, 'Error creating camera: invalid coordinate format.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, 'Error occurred while creating the camera. Please check the coordinates.')

    return render(
        request,
        'projects/add_cam.html',
        {
            'project_name': zone_instance.name_project.name,
            'zone_name': zone_instance.name_zone,
            'zones': zones,
            'cams': cams,
            'zones_data': zones_data,
            'cams_data': cams_data,
        }
    )

@login_required
def project_list(request):
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    # Récupérer les projets créés par ce superviseur
    projects = Project.objects.filter(supervisor=request.user)
    
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def delete_project(request, project_id):
    """Delete a project and all its related zones and cameras."""
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")

    project = get_object_or_404(Project, id=project_id, supervisor=request.user)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" has been successfully deleted.')
    
    return redirect('projects:project_list')


@login_required
def project_detail(request, project_id):
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    project = get_object_or_404(Project, id=project_id, supervisor=request.user)
    
    # Get all project zones with their cameras
    zones = Zone.objects.filter(name_project=project).prefetch_related('cameras')
    
    # Calculate total number of cameras
    total_cameras = sum(zone.cameras.count() for zone in zones)
    
    # Convert JSON coordinates to JSON strings for the template
    zones_data = []
    for zone in zones:
        cameras_data = []
        for cam in zone.cameras.all():
            cameras_data.append({
                'cam': cam,
                'coords_json': json.dumps(cam.coords_cam) if cam.coords_cam else 'null'
            })
        zones_data.append({
            'zone': zone,
            'coords_json': json.dumps(zone.coords_polys) if zone.coords_polys else 'null',
            'cameras_data': cameras_data
        })
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'zones_data': zones_data,
        'zones': zones,
        'total_cameras': total_cameras
    })