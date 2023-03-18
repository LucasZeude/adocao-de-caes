from django.shortcuts import render, redirect
from divulgar.models import Pet, Raca
from django.contrib import messages
from django.contrib.messages import constants
from .models import PedidoAdocao
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

@login_required
def listar_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(status="P")
        racas = Raca.objects.all()

        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')

        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter == 'todas':
            raca_filter = Raca.objects.all()
        
        elif raca_filter:
            pets = pets.filter(raca__id=raca_filter)
            raca_filter = Raca.objects.get(id=raca_filter)

        return render(request, 'listar_pets.html', {'pets': pets, 'racas': racas, 'cidade': cidade, 'raca_filter': raca_filter})



@login_required
def pedido_adocao(request, id_pet):
    pet = Pet.objects.get(id=id_pet)
    pets =Pet.objects.filter(id=id_pet).filter(status='P')
    nome = request.POST.get('nome')
    cidade = request.POST.get('cidade')
    telefone = request.POST.get('telefone')
    
  
    if pet.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pet e seu voce não pode solicitar a adoção :)')
        return redirect('/adotar')

    if not pets.exists():
        messages.add_message(request, constants.ERROR, 'Esse pet já foi adotado :)')
        return redirect('/adotar')

    pedido = PedidoAdocao(pet=pets.first(),
                          usuario=pet.usuario,
                          data=datetime.now(),
                          nome=nome,
                          cidade=cidade,
                          telefone=telefone,
                          )               


    pedido.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado, você receberá um e-mail caso ele seja aprovado.')
    return redirect('/adotar')

@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    pet = Pet.objects.get(nome=pedido.pet)
    
    if status == "A":
        pet.status = 'A'
        pedido.status = 'AP'
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'

    pedido.save()
    pet.save()

    
    send_mail(
        'Sua adoção foi processada',
        string,
        'lucaszeude2@outlook.com',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')
