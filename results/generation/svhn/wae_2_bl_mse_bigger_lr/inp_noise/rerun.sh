# 2021-03-02 00:36:09.995928
python train_wae.py --experiment_name=wae_2_bl_mse_bigger_lr/inp_noise --convar_type=naive --inpainter_type=noise --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 4e-4 --wae_bl 2 --wae_recon_loss mse
